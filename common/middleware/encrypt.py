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

        pid = os.fork()
        if pid:
            return self.app(env,start_response)
        else:
            while (True):
                print env.get('HTTP_X_AUTH_TOKEN',None)
                time.sleep(3)
        """resp = req.get_response(self.app)
        resource = resp.body
        x = 0 
        for c in encrypt_resource(str(resp.content_length),key): 
            x += ord(c)

        resp.content_length = x   #crea una lambda function per calcolare x
        resp.content_type = encrypt_resource(str(resp.content_type),key) #sembra un'istruzione inutile (linux riconosce che un file di testo)
        resp.last_modified = encrypt_resource(str(resp.last_modified),key) #sembra un'istruzione inutile (linux mette come ultima modifica la data di quando lo scarichi)
        resp.body = encrypt_resource(resp.body,key)
        if is_success(resp.status_int):
            old_cryptotoken = env.get('swift_crypto_fetch_old_crypto_token',None)
            if old_cryptotoken != None:
                token = crypto_functions.decrypt_resource(old_cryptotoken,crypto_functions.get_privatekey())
                key = crypto_functions.decrypt_resource(crypto_functions.get_cryptokey(),token)
                resource = crypto_functions.decrypt_resource(resp.body,key)
                #Da aggiungere last_modified e content length
            
            #Encrypt resource
            token = env.get('swift_crypto_fetch_new_token',None)
            if token != None:
                cryptokey = crypto_functions.encrypt_resource(crypto_functions.get_key(),token)
                #da terminare
            #return encrypt_response(req,key,resp)

            
        return self.app(env, start_response)       
        """

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
