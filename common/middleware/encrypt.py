from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.container.server import ContainerController
import os, time
import json
from swift.common.http import is_success
from swift.common.swob import wsgify
import crypto_functions as cyf

class encrypt(WSGIContext):

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        print "----------------- ENCRYPT -----------------------"
        req = Request(env)
        print req.method
        ''' 
        #Create request to obtain list object
        new_headers = req.headers
        new_headers.method = "HEAD"
        new_req = Request.blank(req.path_info,None,new_headers,None)
        resp = new_req.get_response(self.app)'''
        print "-----------------List OBJECT--------------------------"
       """ 
        #list_obj = resp.body.split('\n')[:-1]
        req.headers['X-Container-Sysmeta-crypto'] = "Danieleeeeeeeeeeeeeeeee"
        print req.headers
        username   = env.get('HTTP_X_USER_NAME',None)
        resp = req.get_response(self.app)
        req.headers.method = "HEAD"
        req2 = Request.blank(req.path_info,None,req.headers,None)
        resp2 = req2.get_response(self.app)
        print "RESP...................................."
        print resp2.headers
        time.sleep(6)
        """
        #if is_success(resp.status_int):
        if req.method == "POST" and username != "admin" and username != None:
            
            version, account, container, obj = req.split_path(1,4,True)
            new_headers = req.headers
            new_headers.method = "HEAD"
            new_req_head = Request.blank(req.path_info,None,new_headers,None)
            head_resp = new_req_head.get_response(self.app)
            
            old_cryptotoken = env.get('swift_crypto_fetch_old_crypto_token',None)
            if old_cryptotoken != None:
                old_token = cyf.decrypt_resource(old_cryptotoken,cyf.get_privatekey())
                cryptokey = head_resp.headers.get('X-Container-Sysmeta-Crypto-Key',None)
                key = cyf.decrypt_resource(cryptokey,old_token)
                #Da aggiungere last_modified e content length
            else: 
                key = cyf.gen_key()
                list_file = head_resp.body.split('\n')[:-1]
                
                #PUT di un nuovo container con il nome criptato
                #new_headers.method = "PUT"
                #cryptocontainer = cyf.encrypt_resource(container,key)
                #new_path_info = "/".join(version,account,cryptocontainer)
                #new_req_put = Request.blank(new_path_info,None,new_headers,None)
                
                sons_list = []
                for obj in list_file: 
                    pid = os.fork()
                    if pid:
                        sons_list.append(pid)
                    else:
                        print " I AM THE SON! "
                        # get file dalocntainer vecchio, cripto il file, faccio la put del file nel ocntainer criptato  e muoio
                
                #Creo un fratellastro che aspetti tutti i processi che hanno criptato gli oggetti, e cancella il vecchio container
                #pid = os.fork()
                #if not pid:
                #    while sons_list:
                        # cicla finche la lista non è vuota. 
                        # In python-style-guide: per python (strings, lists, tuples) empty are false
                        #time.sleep(3)
                    #lista vuota
                    #cancella il vecchio container e muori
                    

            new_token = env.get('swift_crypto_fetch_new_token',None)
            if new_token != None:
                
                cryptokey = cyf.encrypt_resource(key,new_token)
                
                new_headers['X-Container-Sysmeta-Crypto-Key'] = cryptokey
                new_headers.method = "POST"
                new_req_post = Request.blank(req.path_info,None,new_headers,None)
                
                    
                        
        return self.app(env, start_response)       
        

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
