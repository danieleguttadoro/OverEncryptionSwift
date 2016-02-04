from swift import gettext_ as _

from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.common.swob import wsgify

#To use encswift
import catalog_functions
import crypto_functions as cyf
import time
#To use barbican
import sys
import traceback

#from barbicanclient import client
from keystoneclient import session
from keystoneclient.auth import identity
################

#def acl(obj):
#    if obj == 'object1':
#        return ['142de5b2c87b4827861c536059c97c37','b48877a174e641fc91dd85540e8643b9']
#    elif obj == 'object2':
#        return ['142de5b2c87b4827861c536059c97c37']

def to_do_overencryption():
    # for now, random function to establish if we must do an overencryption. Later, we scan BEL-graph.
    #return random.randint(0,1)
    return 10

def create_head_req(req):
    version, account, container, obj = req.split_path(1,4,True)
    path_info = "/".join(["",version,account,container])
    new_head_req = Request.blank(path_info,None,req.headers,None)
    new_head_req.method = 'HEAD'
    return new_head_req

class key_master(WSGIContext):

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        
        print "----------------- KEY_MASTER -----------------------"
        req = Request(env)
        #barbican_client()
        #COMMENT: Finding user and token
        username   = env.get('HTTP_X_USER_NAME',None)
        userid     = env.get('HTTP_X_USER_ID',None)
        auth_token = env.get('HTTP_X_AUTH_TOKEN',None)
        print "USERNAME ----> ", username
        print "USERID   ----> ", userid
        #COMMENT: Control the author of the request. DA AGGIUNGERE IL CONTROLLO SULL'ID DEL CEILOMETER(OMONOMIA con un utente)
        if username != "ceilometer" and username != "admin" and username != None and req.method != 'PUT':
            container = req.split_path(1,4,True)[2]
	        #Get the catalog from metacontainer
            found_meta_container, json_catalog = catalog_functions.get_catalog(self.app,auth_token,req,userid,username)        
            if req.method == "GET" and json_catalog != None and found_meta_container != None:
                #COMMENT: if json_catalog == None, overencrypt never done
                #COMMENT: if found_meta_container == None, not exist a catalog	
                #COMMENT: Scan the graph to obtain the key and insert it in the env (GET) or to modify the graph in order to add or delete a key (PUT)
                graph =  catalog_functions.load_graph(json_catalog)
                cryptotoken = catalog_functions.get_cryptotoken(graph,container) 
                if cryptotoken != None:
	                #COMMENT: Setto il cryptotoken per renderlo disponibile al decrypt
                    #env['swift_crypto_fetch_crypto_token'] = "XZmBROlPFEZbfTn0PPGKVwen5MCct56FtOM/XFaDg62DEW85MOhYz+8KXiwj15itgxFvOTDoWM/vCl4sI9eYrQ=="
                    env['swift_crypto_fetch_crypto_token'] = cryptotoken
                    #COMMENT: Richiedo la cryptokey relativa al container e la inserisco nell'environ per il decrypt
                head_req = create_head_req(req)
                head_resp = head_req.get_response(self.app)
                #env['swift_crypto_fetch_crypto_key'] = "lFcV0dBnmWXzrJh2WaME4wen5MCct56FtOM/XFaDg62DEW85MOhYz+8KXiwj15itgxFvOTDoWM/vCl4sI9eYrQ=="
                env['swift_crypto_fetch_crypto_key'] = head_resp.headers.get('x-container-sysmeta-crypto-key',None)
                    	     
            elif req.method== "POST":
                if to_do_overencryption():         
                    #LISTA ABC DA RICAVARE DALLA MODIFICA DELLA ACL O DA OVERENCRYPT
                    token = cyf.gen_token()
                    node = catalog_functions.create_node(container,req.headers.get('x-container-meta-acl-label',None),
                                                            token,userid)
                    catalog_functions.send_message("INSERT",userid,node)
                    #Encrypt the resource
                    if json_catalog != None:
                        graph =  catalog_functions.load_graph(json_catalog)
                        old_cryptotoken = catalog_functions.get_cryptotoken(graph,container)
                        env['swift_crypto_fetch_old_crypto_token'] = old_cryptotoken
                    env['swift_crypto_fetch_new_token'] = token
                else:
                    if json_catalog != None:
                        graph = catalog_functions.load_graph(json_catalog)
                        node = catalog_functions.get_node(graph,container)
                        if node != None:
                            catalog_functions.send_message("REMOVE",userid,node)
                            cryptotoken = node['CRYPTOTOKEN']
                            token = cyf.decrypt_resource(cryptotoken,cyf.get_privatekey())
                            
                            new_req = create_head_req(req)
                            head_resp = new_req.get_response(self.app)
                            cryptokey = head_resp.headers.get('x-container-sysmeta-crypto-key',None)
                            key = cyf.decrypt_resource(cryptokey,token)

                            new_req.headers['x-container-sysmeta-crypto-key'] = key
                            new_req.method = 'POST'
                            new_req.get_response(self.app)
                            		       
                                
            elif req.method == "DELETE":
	            #TODO
      
	            pass
        
        return self.app(env, start_response)


def barbican_client():

    #Variables for barbican
    ADMIN_USER="admin"
    ADMIN_PASS="secretsecret"
    ADMIN_TENANT="demo"
    AUTH_URL="http://127.0.0.1:5000/v2.0"
    BARB_URL="http://127.0.0.1:9311"
    AUTH_IP="127.0.0.1"
	
    try:
        # We'll use Keystone API v3 for authentication
        auth = identity.v2.Password(auth_url=AUTH_URL,
            username=ADMIN_USER,
            password=ADMIN_PASS,
            tenant_name=ADMIN_TENANT)

        # Next we'll create a Keystone session using the auth plugin we just created
        sess = session.Session(auth=auth)

        print '-----------------------BARBICAN---------------------------'
        print 'session created successfully'

        # Now we use the session to create a Barbican client
        barbican = client.Client(endpoint=BARB_URL, session=sess)

        print 'barbican client created successfully'

        # Let's create a Secret to store some sensitive data
        secret = barbican.secrets.create(name=u'Self destruction sequence',
                                         payload=u'the magic words are squeamish ossifrage')

        print 'secret created successfully'

        # Now let's store the secret by using its store() method. This will send the secret data
        # to Barbican, where it will be encrypted and stored securely in the cloud.
        secret.store()
        #u'http://localhost:9311/v1/secrets/85b220fd-f414-483f-94e4-2f422480f655'

        print 'secret stored successfully'

        # The URI returned by store() uniquely identifies your secret in the Barbican service.
        # After a secret is stored, the URI is also available by accessing
        # the secret_ref attribute.
        print(secret.secret_ref.replace('localhost',AUTH_IP))
        #http://localhost:9311/v1/secrets/091adb32-4050-4980-8558-90833c531413

        # When we need to retrieve our secret at a later time, we can use the secret_ref
        retrieved_secret = barbican.secrets.get(secret.secret_ref.replace('localhost',
            AUTH_IP))
        # We can access the secret payload by using the payload attribute.
        # Barbican decrypts the secret and sends it back.
        print(retrieved_secret.payload)
        #the magic words are squeamish ossifrage

    except:
        traceback.print_exc(file=sys.stdout)
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
