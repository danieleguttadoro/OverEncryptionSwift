from swift import gettext_ as _
from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.common.swob import wsgify,HTTPUnauthorized
import time, ast, json
#To use encswift
from catalog_manager import *
from connection import *
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as kc

class key_master(WSGIContext):

    def extractACL(self, headers):
        """
        Extract the ACL from the container headers
        """
        # Get ACLs from the headers
        if headers.has_key('x-container-read'):
            acl_read = ast.literal_eval(headers['x-container-read'])
        elif headers.has_key('X-Container-Read'):
            acl_read = ast.literal_eval(headers['X-Container-Read'])
        else:
            acl_read = {}
        if headers.has_key('x-container-write'):
            acl_write = ast.literal_eval(headers['x-container-write'])
        elif headers.has_key('X-Container-Write'):
            acl_write = ast.literal_eval(headers['X-Container-Write'])
        else:
            acl_write = {}
        acl = reduce(lambda x, y: x + y, acl_read.values(), []) + reduce(lambda x, y: x + y, acl_write.values(), [])
        # Remove duplicates:
        acl = list(set(acl))
        # Remove AUTH_ from names
        acl_clean = map(lambda x: x.replace('AUTH_', ''), acl)
        return acl_clean

    def getUserID(self):
        """
        Get the user's ID from Keystone
        """
        # Requires an admin connection
        auth = v3.Password(auth_url=AUTH_URL,username=ADMIN_USER, password=ADMIN_KEY,project_name='demo',user_domain_name='Default',project_domain_name='Default')
        sess = session.Session(auth=auth)
        keystone = kc.Client(session=sess)
        this_user = filter(lambda x: x.name == self.name, keystone.users.list())
        return this_user[0].id

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf
        self.name = SWIFT_USER
        self.userID = self.getUserID()

    def __call__(self, env, start_response):
        
        req = Request(env)
        username   = env.get('HTTP_X_USER_NAME',None)
        userid     = env.get('HTTP_X_USER_ID',None)
        tenant     = env.get('HTTP_X_PROJECT_NAME',None)
        version, account, container, obj = req.split_path(1,4,True)
        #COMMENT: Control the author of the request. 
        if req.method == "PUT" and req.headers.get('x-container-read',None) is not None and  container is not None and obj is None:
                #Associate owner to container
                req.headers['x-container-sysmeta-owner'] = userid
                req.headers['x-container-meta-owner'] = userid
        if req.method =="POST" and req.headers.get('x-container-read',None) is not None:
                new_req = Request.blank(req.path_info,None,req.headers,None)
                new_req.method = "HEAD"
                new_req.path_info = "/".join(["",version,account,container])
                new_resp = new_req.get_response(self.app) 
                if new_resp.headers.get('x-container-meta-bel-id',None) is None:
                    #Container public -> private. Associate owner
                    req.headers['x-container-sysmeta-owner'] = userid
                    req.headers['x-container-meta-owner'] = userid
                elif new_resp.headers.get('x-container-sysmeta-owner',None) != userid:
                    #Container already private and user is not the owner
                    return HTTPUnauthorized(body="Unauthorized")(env, start_response)
        if req.method == "GET" and username != "ceilometer" and username != None:
            if obj != None:
                #Request a container
                new_req = Request.blank(req.path_info,None,req.headers,None)
                new_req.method = "HEAD"
                new_req.path_info = "/".join(["",version,account,container])
                response = new_req.get_response(self.app)
                cont_header = response.headers
                container_sel_id = cont_header.get('x-container-meta-sel-id',None)
                cont_secret_ref = cont_header.get('x-container-meta-container-ref',None)
                env['swift_crypto_fetch_cont_id'] = container_sel_id    
                resp_obj = req.get_response(self.app)
                object_sel_id = resp_obj.headers.get('x-object-meta-sel-id',None)
                if object_sel_id != container_sel_id:# and onResource=="False":
                    #The object has been uploaded before the last policy change
                    if object_sel_id is not None:
                        old_dek = get_secret(self.userID,cont_secret_ref,object_sel_id,tenant).get('KEK',None)
                        if old_dek is not None:
                            env['swift_crypto_old_fetch_key'] = old_dek
                        else:
                            env['swift_crypto_old_fetch_key'] = "NotAuthorized"
                    if container_sel_id is not None: 
                        dek = get_secret(self.userID,cont_secret_ref,container_sel_id,tenant).get('KEK',None)
                        if dek is not None:
                            env['swift_crypto_fetch_key'] = dek
                        else:
                            env['swift_crypto_fetch_key'] = "NotAuthorized"  
            """elif obj == None and container == None:
                resp_account = req.get_response(self.app)
                list_containers = resp_account.body
                list_containers = json.loads(list_containers)
                for cont in list_containers:
                    new_req = Request.blank(req.path_info,None,None,None)
                    new_req.method = "GET"
                    cont_name = cont.get('name','') 
                    new_req.path_info = "/".join(["",version,account,cont_name])
                    response = new_req.get_response(self.app)
                    print response.headers
                    print cont
                    print "-----------------------"
                    list_acl = self.extractACL(response.headers)
                    if list_acl != [] and userid not in list_acl:
                        print "list_acl\n"
                        print list_acl
                        list_containers.remove(cont)
                resp_account.body = json.dumps(list_containers)"""
        return self.app(env, start_response)

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
