from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError, wsgify
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info
import catalog_functions
import crypto_functions as cyf

class decrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   @wsgify
   def __call__(self, req):
        print "----------------- DECRYPT -----------------------"
               
        resp = req.get_response(self.app)
        cryptotoken = req.environ.get('swift_crypto_fetch_crypto_token',None)
        print "|||||||||||||||||||||||||||||||||||||||||||"
        print resp.body
        if cryptotoken != None:
            print "----------------------CRYPTOTOKEN VALID --------------------------"
            token = cyf.decrypt_resource(cryptotoken,cyf.get_privatekey())
            key = cyf.decrypt_resource(cyf.get_cryptokey(),token)
            response = cyf.decrypt_resource(resp.body,key)
            last_modified = cyf.decrypt_resource(resp.last_modified,key)
            resp.content_lenght = len(resp.body)
	    
        return resp  

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return decrypt(app,conf)
    return except_filter
