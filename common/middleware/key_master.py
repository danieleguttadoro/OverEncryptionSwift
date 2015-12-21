from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info
class key_master(WSGIContext):

   meta_container = "meta"
   graph_tokens = "b"

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf

   def __call__(self, env, start_response):
        print "-----------------KEYMASTER-----------------------"
	req = Request(env)

	#COMMENT: Finding user
        username = env.get('HTTP_X_USER_NAME',None)
        userid = env.get('HTTP_X_USER_ID', None)
        print username
        print userid
        print req.headers
        print req.body
        
	#print "KEYS-------->>>>>>>>"
        #print env.keys()
        #print "ENDKEYS------->>>>>>>"     

	#COMMENT: Obtaining versione and account of the Request, to do another Request and obtain the graph of tokens 
	version, account, container, obj = req.split_path(1,4,True)  
	path_meta = "/".join(["", version , account , self.meta_container, self.graph_tokens])  
	print path_meta
	req_meta = Request.blank(path_meta,None,req.headers,None)
	graph = req_meta.get_response(self.app)
	print graph.body
        
	
	#COMMENT: Scan graph to obtain the key and insert it in the env

	#Fake modify of the graph
        new_graph = graph
        new_graph.body = "Nuova Modifica: STIAMO LAVORANDO BENE"
        ##print new_graph
        ##print new_graph.headers
        ##print new_graph.body

        #COMMENT: Upload on metacontainer the new version of graph

		
	print "-------------------------END-------------------------------"
        return self.app(env, start_response)       

"""        for a in env.keys():
                print "---------------NEXT KEY------------------" + a 
                print env[a]
                if a=='HTTP_X_USER_NAME':
                        print "USERNAME ----> " + env['HTTP_X_USER_NAME']
                        break
                if a=='HTTP_X_USER_ID':
                        print "USERID ----> " + env['HTTP_X_USER_ID']
                        continue
        print env """


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
