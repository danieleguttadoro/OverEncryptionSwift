from swift import gettext_ as _
import md5
import time
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
        
        print "----------------- ENCRYPT -----------------------"
        
        resp = req.get_response(self.app)
        env = req.environ
        username = env.get('HTTP_X_USER_NAME',None)
        
        if req.method == "GET" and username != 'admin' and username != None:               
            
            token = req.environ.get('swift_crypto_fetch_token',None)       
            
            if token != None:
                resp.body = cyf.decrypt_resource(resp.body,token) 
                resp.headers['Etag'] = md5.new(resp.body).hexdigest()
                #last_modified = cyf.decrypt_resource(resp.last_modified,token)
                resp.content_lenght = len(resp.body)  
        
        return resp 
         

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return decrypt(app,conf)
    return except_filter
