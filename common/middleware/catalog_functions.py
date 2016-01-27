#!/uisr/bin/env python

import json, time
import base64
from itertools import *
from swift.common.swob import Request
import pika
from swift.proxy.controllers.base import Controller

from keystoneclient.v2_0 import client
from keystoneclient.exceptions import Unauthorized

def gen_token():
    return "aaa"

def conn_keystone(username,userid,auth_token):
    try:
        keystone = client.Client(username=username,token = auth_token,tenant_name=userid,auth_url="http://127.0.0.1:5000/v2.0")
        return keystone.tenant_id 
    except Unauthorized:
        return None
		
#modified on server
def get_catalog(app,auth_token,req,user_id,username):
    #COMMENT: Obtaining version and account of the Request, to do another Request and obtain the graph of tokens
    #version, account, container, obj = req.split_path(1,4,True)
    account = conn_keystone(username,user_id,auth_token)
    if account == None:
    	return None, None
    path_catalog = "/".join(["", "v1" , account , user_id, user_id])
    
    req_catalog = Request.blank(path_catalog,None,req.headers,None)
    res_catalog = req_catalog.get_response(app)
    if res_catalog.status =='404 Not Found':
        return 'Found', None
    return 'Found', res_catalog.body

def create_node(node_child,acl_child,cryptotoken,ownertoken):
    Entry = {}
    Entry["NODE_CHILD"] = node_child
    Entry["ACL_CHILD"] = stringTOlist(acl_child)
    #TokenDecEscape = r"%s" % upd_details[7].decode('string-escape')
    Entry["CRYPTOTOKEN"] = cryptotoken# TokenDecEscape
    Entry["OWNERTOKEN"] = ownertoken
    #Entry["VERSIONTOKEN"] = '0'        # Left for future development
    #Entry["TYPE"] = 'USER'
    return Entry

#added in server
def add_node(graph,Entry,parent,userid):
    # New node
    Parent = [elem for elem in graph if elem.has_key('NODE') and elem['NODE'] == parent ]
    if len(Parent) == 0:
        # No token exiting from current node exist, also the parent node must be created
        CatGrEntry = {}
        CatGrEntry["NODE"] = parent
        CatGrEntry["ACL"] = parent
        CatDtEntryList = []
        CatDtEntryList.append(Entry)
        CatGrEntry["TOKEN"] = CatDtEntryList
        graph['NODES']=CatGrEntry
    else:
	    # The source node already exists. Only the destination+token must be appended
        for elem in [elem for elem in graph if elem['NODE'] == parent]:
            Parent[0]['TOKEN'].append(Entry)
    
    return graph

#Not used?
def get_graph(json_data_catalog):
    """
    Read the catalog (simple version, without further browse) and build the graph.
    Args:
        json_data_catalog: the catalog .json
    Returns:
        CatGraph:
    """
    json_data = json.loads(json_data_catalog.decode('latin-1'), strict=False)
    CatGraph = []

    def foo(x):
        for child in x['TOKEN']:
	        pass
            #child['NODE'] = x['NODE']
            #child['ACL'] = x['ACL']
        return x['TOKEN']

    CatGraph = map(foo, json_data['NODES'])
    CatGraph = list(chain.from_iterable(CatGraph))
    return CatGraph


def load_graph(json_data_catalog):
    """
    Load the graph from the catalog.
    This function differs from 'get_graph' because there are no information
    on nodes father (i.e. keys NODE and ACL)
    Args:
        usrID: the ID of the user
    Returns:
        The graph as a list of nodes (a list of dictionaries)
    """
    json_cat = json.loads(json_data_catalog)
    return json_cat['NODES']


def get_node(graph, destination):
    """
    Args:
        graph: the graph seen by the user (obtained by load_graph)
        container
    Returns:
        the path from the root to the destination node
    """
	
    currDestination = destination
    for elem in graph:
       if elem.has_key('TOKEN'):
         entry = elem['TOKEN']
         for ent in entry:	
          if currDestination == ent['NODE_CHILD']:
            if tokenIsValid(ent['CRYPTOTOKEN'], ent['OWNERTOKEN']):
               return ent
    return None

#NoT USED
def majorChild(graph, new_node_Acl):
    """
    Get the parent node of the new node (it may be a child node itself)
    Args:
        graph: the graph seen by the user
        new_node_Acl: the ACL of the new node
    Returns:
        majChl: the parent node
        majChlACL: the parent node's ACL
    """
    majChl = None
    majChlACL = None
    majChlDim = None
    for node in graph:
        # If there are elements in discard list, this node cannot be parent of the new node
        discard = filter(lambda x: x not in new_node_Acl.split(':'), node['ACL_CHILD'].split(':'))
        if not discard:
            if len(node['ACL_CHILD'].split(':')) >= majChlDim:
                majChlDim = len(node['ACL_CHILD'].split(':'))
                majChl = node['NODE_CHILD']
                majChlACL = node['ACL_CHILD']
    return majChl, majChlACL

def remove_node(graph,container):
    currContainer = container
    for elem in graph:
        if elem.has_key('TOKEN'):
            entry = elem['TOKEN']
            for ent in entry:
                if currContainer == ent['NODE_CHILD']:
                    entry.remove(ent)

    return graph

#NOT USED
def browsePath(userID, MyPath):
    """
    Browse a path and derive the token.
    Returns:
        k: the decrypted message
        lastOwnerToken: who generated the token
    """
    k = None
    for step in MyPath:
        if not k:
            # First arch (or single arch
            #PROVA
            k = step['CRYPTOTOKEN']	
            #k = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
            #sender=step['OWNERTOKEN'], receiver=userID)
            k_prec = k
        else:
            token_ciph = step['CRYPTOTOKEN']
            #token_ciph = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
            # sender=step['OWNERTOKEN'], receiver=userIDi
            #k = decrypt_msg(base64.b64decode(token_ciph), k_prec)
            k = step['CRYPTOTOKEN']
            k_prec = k
            lastOwnerToken = step['OWNERTOKEN']

    return k, lastOwnerToken


def tokenIsValid(token, owner):
    """
    Control the validity of a token. Left for future implementation.
    Returns:
        True if the token is valid, false otherwise
    """
    return True

def get_cryptotoken(catalog, container):
    myPath = get_node(load_graph(catalog), container)
    if myPath == None:
        return None
    
    return myPath['CRYPTOTOKEN']

def compose_graph(graph,userid):
     Entry = {}
     Entry["TYPE_ENTITY"] = "USER"
     Entry["ID_ENTITITY"] = userid
     Entry["NODES"] = graph
     return json.dumps(Entry, indent=4, sort_keys=True)
 

def new_cryptotoken(node):
    #TODO
    return "aaaaaaaa4"


    #def overencrypt(user,catalog,container_list,acl_list):overencrypt non sappiamo se container list viene passato singolarmente o come ua lista d container
    #    global graph
    #    graph = load_graph(catalog)
    #    new_acl_list = ':'.join(sorted(acl_list))
    #    for elem in container_list:
    #	    cryptotoken = new_cryptotoken(userid)
    #	    graph = remove_node(graph,elem,userid)
    #	    node = create_node(elem,new_acl_list,cryptotoken,userid)
    #	    graph = add_node(graph,node,userid,userid)
    #    return graph

def stringTOlist(list_string):
    res = list_string.split(":")
    return res
    

def listTOstring(list):
    return '[' + ':'.join(sorted(list)) + ']'

def send_message(command,userid,node):
                
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='daemon1', durable=True)
       
    channel.confirm_delivery()
 
    print " *********** Send Message *************"
    node_s = json.dumps(node, indent=4, sort_keys=True)
    msg = command +"#"+ userid + "#" + node_s
    try:  
        channel.basic_publish(exchange='',
                              routing_key='daemon',
                              body=msg,
                              properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
        
        print(" [x] Sent [%s]" % msg)
    except pika.exceptions.ConnectionClosed as exc:
        print('Error. Connection closed, and the message was never delivered.')

    connection.close()

    return

