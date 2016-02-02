from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext

import os, time

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

        #if is_success(resp.status_int):
        """if req.method = "POST":

            old_cryptotoken = env.get('swift_crypto_fetch_old_crypto_token',None)
            if old_cryptotoken != None:
                # ottengo lista dei file o metadati o cosa? Con get_container
                #resp = req.get_response(self.app)
                token = cyf.decrypt_resource(old_cryptotoken,cyf.get_privatekey())
                #ottenere cryptokey con richiesta HEAD al container
                key = cyf.decrypt_resource("prova",token)
                #resource = cyf.decrypt_resource(resp.body,key)
                #Da aggiungere last_modified e content length
            else: 
                key = cyf.gen_key()
                #cripto tutti i file all'interno del container con la key
                #for file in lista_file_container 
                    pid = os.fork()
                    if pid:
                        #tramite HEAD ottengo le info (nome, size, ..) del container, le cripto con la key, e faccio POST dopo (1)
                    else:
                        # I AM THE SON!
                        # cripto il file, faccio la put  e muoio

            new_token = env.get('swift_crypto_fetch_new_token',None)
            if new_token != None:
                
                cryptokey = cyf.encrypt_resource(key,new_token)
                # (1) aggiungo cryptokey come metadato e tramite POST salvo tutti container-metadata
                    
        """                
        return self.app(env, start_response)       
        

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
