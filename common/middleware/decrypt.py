from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info
import catalog_functions
import crypto_functions

class decrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf

   def __call__(self, env, start_response):
        print "----------------- DECRYPT MODULE -----------------------"
        req = Request(env)
        #resp deve essere fatta, ma qui e' commentata in modo da effettuare una sola richiesta del key_master.
        #resp = req.get_response(self.app)
        cryptotoken = env.get('swift_crypto_fetch_crypto_token',None)
        print cryptotoken
        if cryptotoken != None:
            print "----------------------CRYPTOTOKEN VALID --------------------------"
            token = decrypt_resource(cryptotoken,crypto_functions.get_privatekey())
            key = decrypt_resource(crypto_functions.get_cryptokey(),token)
            response = decrypt_resource(resp.body,key)
            last_modified = decrypt_resource(resp.last_modified,key)
            resp.content_lenght = len(resp.body)
	    
        return self.app(env, start_response)  

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return decrypt(app,conf)
    return except_filter
