from swift import gettext_ as _

from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.common.swob import wsgify

#To use encswift
from catalog_functions import *
import time

from keystoneclient import session

DAEMON_IP = '127.0.0.1'
class key_master(WSGIContext):

    userID = "a1882078338d4ed1840ad1c7e8745537" 

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        
        print "----------------- KEY_MASTER -----------------------"
        req = Request(env)
        
        username   = env.get('HTTP_X_USER_NAME',None)
        userid     = env.get('HTTP_X_USER_ID',None)
        print "USERNAME ----> ", username
        print "USERID   ----> ", userid
        
        #COMMENT: Control the author of the request. DA AGGIUNGERE IL CONTROLLO SULL'ID DEL CEILOMETER(OMONOMIA con un utente)
        if req.method == "GET" and username != "ceilometer" and username != "encadmin" and username != "admin" and username != None:
            
            version, account, container, obj = req.split_path(1,4,True)

        
            new_req = req
            new_req.method = "HEAD"
            new_req.path_info = "/".join(["",version,account,container])
            response = new_req.get_response(self.app)
            cont_header = response.headers
            acl = cont_header.get('x-container-meta-acl-label',"")
            sel_label = cont_header.get('x-container-sel-label',"")

            if sel_label is not "":
                #Add swift id to manage overencryption
                acl = acl + ":" + self.userID
                acl_list = sorted(acl.split(':'))
                key = get_token_sel(self.userID,acl_list)
                if key is not None:
                    print('Decryption token found')
                    env['swift_crypto_fetch_token'] = key        

        return self.app(env, start_response)

def receive_message(userid):

    connection = pika.BlockingConnection(pika.ConnectionParameters(DAEMON_IP))
    channel = connection.channel()
    channel.queue_declare(queue='swift_'+userid, durable=True)
           
    channel.basic_qos(prefetch_count=1)    
    channel.basic_consume(receive_message,
                      queue='swift_'+userid)

    print(' Waiting for messages [%d] ...' % userid)
    channel.start_consuming()

def receive_message(ch, method, properties, body):
        
    #COMMENT: Setto il cryptotoken per renderlo disponibile all' encrypt
    if body != None:
        token = cyf.decrypt_resource(body,cyf.get_privatekey())
    else: 
        token = None
    env['swift_crypto_fetch_token'] = token

    return

def send_message(userid,container):
                
    connection = pika.BlockingConnection(pika.ConnectionParameters(DAEMON_IP))
    channel = connection.channel()
    channel.queue_declare(queue='daemon_get_swift', durable=True)
       
    channel.confirm_delivery()
    msg = 'GET_CRYPTOTOKEN' + '#' + userid + '#' + container

    try:  
        channel.basic_publish(exchange='',
                              routing_key='daemon_get_swift',
                              body=msg,
                              properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
        
        print(" Sent [%s]" % msg)
    except pika.exceptions.ConnectionClosed as exc:
        print('Error. Connection closed, and the message was never delivered.')

    connection.close()

    return

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
