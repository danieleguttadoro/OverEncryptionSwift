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
        
        #list_obj = resp.body.split('\n')[:-1]
        print req.headers
        req.headers['coglione1'] = "Daniele"
        username   = env.get('HTTP_X_USER_NAME',None)
        resp = req.get_response(self.app)
        req.headers.method = "GET"
        resp2 = req.get_response(self.app)
        print "RESP...................................."
        print resp2.headers
        '''
        #if is_success(resp.status_int):
        if req.method == "ttPOST" and username != "admin" and username != None:

            old_cryptotoken = env.get('swift_crypto_fetch_old_crypto_token',None)
            if old_cryptotoken != None:
                
                #resp = req.get_response(self.app)
                token = cyf.decrypt_resource(old_cryptotoken,cyf.get_privatekey())
                #ottenere cryptokey con richiesta HEAD al container
                key = cyf.decrypt_resource("prova",token)
                #Da aggiungere last_modified e content length
            else: 
                key = cyf.gen_key()
                #HEAD metadati del container e post Dopo
                new_req.headers.method = "HEAD"
                resp = new_req.get_response(self.app)
                #PUT di un nuovo container con il nome criptato
                for obj in list_obj: 
                    pid = os.fork()
                    if not pid:
                        print " I AM THE SON! "
                        # get file dalocntainer vecchio, cripto il file, faccio la put del file nel ocntainer criptato  e muoio
                #Creo un fratellastro che aspetti tutti i processi che hanno criptato gli oggetti, e cancella il vecchio container
                
            new_token = env.get('swift_crypto_fetch_new_token',None)
            if new_token != None:
                
                cryptokey = cyf.encrypt_resource(key,new_token)
                # (1) aggiungo cryptokey come metadato, e tramite POST salvo tutti container-metadata
                    
        '''                
        return self.app(env, start_response)       
        

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
