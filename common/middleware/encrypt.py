from swift import gettext_ as _
import md5
import time
from swift.common.swob import Request, HTTPServerError, wsgify
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info
from crypto_functions import *

class encrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   @wsgify
   def __call__(self, req):
        
        print "----------------- ENCRYPT -----------------------"
        resp = req.get_response(self.app)
        print "aspettando....."
        env = req.environ
        username = env.get('HTTP_X_USER_NAME',None)
        if req.method == "GET" and username!= 'ceilometer' and username != 'admin' and username != 'encadmin' and username != None:               
            
            token = req.environ.get('swift_crypto_fetch_token',None)       
            if token != None:
                print "encrypt - token not none"
                print token
                resp.body = encrypt_msg(str(resp.body),token) 
                resp.headers['Etag'] = md5.new(resp.body).hexdigest()
                #last_modified = cyf.decrypt_resource(resp.last_modified,token)
                resp.content_length = len(resp.body)  
        return resp
         

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
