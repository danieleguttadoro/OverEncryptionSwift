import pika
import json
import logging
import swiftclient
from swift.common.middleware.connection import *
from rabbit_connection import *
from itertools import *
from swift.common.middleware.catalog_functions import *

# set logger info to INFO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

MSG_SERVICE_SRV = IP
MSG_QUEUENAME = QUEUE
MSG_QUEUENAME_SEL = QUEUE_SEL

class RabbitReceiver_Sel:



    def __init__(self):

        self.swift_conn = swiftclient.client.Connection(user=USER, key=KEY, authurl=AUTHURL,

                                                        tenant_name=META_TENANT_SEL, auth_version='2.0')



    def rec_updcat(self, empty=None):

        """

        Get info for the swift connection (NEED AdminRole user)

        """

        logger.info('MSG_SERVICE_SRV> %s ', MSG_SERVICE_SRV)

        logger.info('MSG_QUEUENAME  > %s ', MSG_QUEUENAME_SEL)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=MSG_SERVICE_SRV))

        channel = connection.channel()

        channel.queue_declare(queue=MSG_QUEUENAME_SEL, durable=True)



        print ' [*] Waiting for logs. Press CTRL+C to exit'



        def callback(ch, method, properties, body):

            body_detail = body.split('#')

            if body_detail[0] == 'UPDCAT':

                logger.info("Srv_Msgs: message for updating catalog")

                self.upd_cat_details(body_detail)

            elif body_detail[0] != 'UPDCAT':

                logger.warning("Unknown message")

            ch.basic_ack(delivery_tag=method.delivery_tag)



        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(callback, queue=MSG_QUEUENAME_SEL)

        channel.start_consuming()



    def add_node(self, upd_details):

        """

        Manage ADD_NODE messages.



        Message format:



            UPDCAT#ADD_NODE#<dest>#<node>#<aclnode>#<child>#<aclchild>#<cryptoken>#<ownertoken>



               0      1        2      3       4        5         6          7           8



        Args:



            upd_details: the message



        """

        logger.info("NEW_NODE %s (token from %s : %s )" % (upd_details[5], upd_details[3], upd_details[7]))

        # Format received: UPDCAT#ADD_NODE#<dest>#<node>#<aclnode>#<child>#<aclchild>#<cryptoken>#<ownertoken>

        #                     0      1        2      3       4        5         6          7           8

        # Already existing nodes

        CatGraphAgg = []

        CatGraphAgg = load_graph(upd_details[2])



        # New node

        Parent = [elem for elem in CatGraphAgg if elem['NODE'] == upd_details[3]]



        # Element to be appended

        CatDtEntry = {}

        CatDtEntry["NODE_CHILD"] = upd_details[5]

        CatDtEntry["ACL_CHILD"] = upd_details[6]

        TokenDecEscape = r"%s" % upd_details[7].decode('string-escape')

        CatDtEntry["CRYPTOTOKEN"] = TokenDecEscape

        CatDtEntry["OWNERTOKEN"] = upd_details[8]

        CatDtEntry["VERSIONTOKEN"] = '0'        # Left for future development

        CatDtEntry["TYPE"] = 'USER'

        if len(Parent) == 0:

            # No token exiting from current node exist, also the parent node must be created

            CatGrEntry = {}

            CatGrEntry["NODE"] = upd_details[3]

            CatGrEntry["ACL"] = upd_details[4]

            CatDtEntryList = []



            CatDtEntryList.append(CatDtEntry)

            CatGrEntry["TOKEN"] = CatDtEntryList

            CatGraphAgg.append(CatGrEntry)

        else:

            # The source node already exists. Only the destination+token must be appended

            CatGrEntry = {}

            CatGrEntry["NODE"] = upd_details[3]

            CatGrEntry["ACL"] = upd_details[4]

            for elem in [elem for elem in CatGraphAgg if elem['NODE'] == upd_details[3]]:

                Parent[0]['TOKEN'].append(CatDtEntry)



        Entry = {}

        Entry["TYPE_ENTITY"] = "USER"

        Entry["ID_ENTITITY"] = upd_details[2]

        Entry["NODES"] = CatGraphAgg

        CatContainer = '.Cat_usr%s' % upd_details[2]

        CatSource = '$cat_graph%s.json' % upd_details[2]

        EntryWrite = Entry

        try:

            self.swift_conn.delete_object(CatContainer, CatSource)

            self.swift_conn.put_object(CatContainer, CatSource, json.dumps(EntryWrite, indent=4, sort_keys=True), content_type='application/json')

            logger.info("New node added to the graph.")

        except:

            logger.error('Error Rabbit msg received: add node')



    def remove_node(self, upd_details):

        """



        Manage DROP_NODE messages.

        Message format:



            UPDCAT#DROP_NODE#<dest>#<node>#<aclnode>#<ownertoken>



               0       1        2      3       4          5



        Args:



            upd_details: the message



        """

        logger.info("DROP_NODE %s of user %s (message from %s)" % (upd_details[3], upd_details[2], upd_details[5]))

        graph = []

        graph = load_graph(upd_details[2])

        father = (filter(lambda x: x['NODE'] == upd_details[3], graph))

        if father:

            father = father[0]

            children = father['TOKEN']

            for node in graph:

                tokens = node['TOKEN']

                for tok in tokens:

                    if tok['ACL_CHILD'] == father['ACL']:

                        # Found grandfather

                        tokens.remove(tok)

                        # Append children to grandfather

                        node['TOKEN'] = node['TOKEN'] + children

            graph.remove(father)

        else:

            for node in graph:

                tokens = node['TOKEN']

                for tok in tokens:

                    if tok['NODE_CHILD'] == upd_details[3] and tok['ACL_CHILD'] == upd_details[4]:

                        tokens.remove(tok)

                if len(tokens) == 0:

                    # The node to be deleted was only child. Remove its dependancy.

                    graph.remove(node)



        Entry = {}

        Entry["TYPE_ENTITY"] = "USER"

        Entry["ID_ENTITITY"] = upd_details[2]

        Entry["NODES"] = graph

        CatContainer = '.Cat_usr%s' % upd_details[2]

        CatSource = '$cat_graph%s.json' % upd_details[2]

        EntryWrite = Entry

        try:

            self.swift_conn.delete_object(CatContainer, CatSource)

            self.swift_conn.put_object(CatContainer, CatSource, json.dumps(EntryWrite, indent=4, sort_keys=True), content_type='application/json')

            logger.info("Node removed from container.")

        except:

            logger.error('Error Rabbit msg received: remove node')



    def upd_cat_details(self, upd_details):

        """

        Update catalog with new details.



        Message format:



            UPDCAT#ACTION#...



               0      1

        Args:



            upd_details: the message received from Rabbit



        """

        if upd_details[1] == "ADD_NODE":

            try:

                self.add_node(upd_details)

            except:

                logger.error("Error Rabbit in add node")

            logger.info("-" * 35)

        elif upd_details[1] == "DROP_NODE":

            try:

                self.remove_node(upd_details)

            except:

                logger.error("Error Rabbit in drop node")

            logger.info("-" * 35)

        elif upd_details[1] == "DROP_TOKEN":

            logger.info("Delete token. Not implemented")

            logger.info("-" * 35)
