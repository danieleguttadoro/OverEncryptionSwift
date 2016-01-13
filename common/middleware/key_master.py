from swift import gettext_ as _

from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext

from swift.common.swob import wsgify

class key_master(WSGIContext):

   # Names of meta container and file of the graph
   meta_container = "meta"
   graph_tokens = "b"

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   
   def __call__(self, env, start_response):
      print "----------------- KEY_MASTER -----------------------"
      
"""        
        req = Request(env)
        resp = req.get_response(self.app)

        #COMMENT: Finding user and method
        username = env.get('HTTP_X_USER_NAME',None)
        #COMMENT: Control the author of the request. DA AGGIUNGERE IL CONTROLLO SULL'ID DEL CEILOMETER(OMONOMIA con un utente)
        if username != "ceilometer":

            #COMMENT: Obtaining version and account of the Request, to do another Request and obtain the graph of tokens 
	        version, account, container, obj = req.split_path(1,4,True)  
	        path_meta = "/".join(["", version , account , self.meta_container, self.graph_tokens])  
	        print path_meta
	        req_meta_container = Request.blank(path_meta,None,req.headers,None)
	        req_graph = req_meta_container.get_response(self.app)
	        print req_graph.body
	     
        	# COMMENT: Scan the graph to obtain the key and insert it in the env (GET) or to modify the graph in order to add or delete a key (PUT)
            # Example: retrieve the key 
            print "Retrieve the key ..."
            key = '01234567890123456789012345678901' # 32 char length

            if key == '':
                raise_error(req,403)
            env['swift_crypto_fetch_crypto_key'] = key

            #COMMENT: Modify the graph
            #Fake modify of the graph
            req_meta_container.body = "Modifica effettuata"

            #COMMENT: Upload on metacontainer the new version of graph
            req_meta_container.method = 'PUT'
            req_meta_container.get_response(self.app)

        return self.app(env, start_response)

@wsgify
def raise_error(req,stat):

    if stat == 403:
        return Response(request=req, status=403, body="USER UNAUTHORIZED TO OBTAIN THIS FILE",
                        content_type="text/plain")

"""
def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
