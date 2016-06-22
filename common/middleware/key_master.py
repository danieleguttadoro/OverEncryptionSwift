from swift import gettext_ as _
from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.common.swob import wsgify,HTTPUnauthorized
import time
#To use encswift
from catalog_manager import *
from connection import *
from keystoneclient import session
from keystoneclient.v2_0 import client as kc

class key_master(WSGIContext):

    def getUserID(self):
        """
        Get the user's ID from Keystone
        """
        # Requires an admin connection
        kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_KEY, tenant_name=TENANT_NAME, auth_url=AUTH_URL)
        this_user = filter(lambda x: x.username == self.name, kc_conn.users.list())
        return this_user[0].id

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf
        self.name = "swift"
        self.userID = self.getUserID()

    def __call__(self, env, start_response):
        
        req = Request(env)
        username   = env.get('HTTP_X_USER_NAME',None)
        userid     = env.get('HTTP_X_USER_ID',None)
        version, account, container, obj = req.split_path(1,4,True)
        #COMMENT: Control the author of the request. 
        if req.method == "PUT" and req.headers.get('x-container-read',None) is not None and  container is not None and obj is None:
                req.headers['x-container-sysmeta-owner'] = userid
                print "PUTRRRRRRRRRRRRRRRRRRRRRRRRRRR"
        if req.method =="POST" and req.headers.get('x-container-read',None) is not None:
                new_req = Request.blank(req.path_info,None,req.headers,None)
                new_req.method = "HEAD"
                new_req.path_info = "/".join(["",version,account,container])
                new_resp = new_req.get_response(self.app) 
                if new_resp.headers.get('x-container-meta-bel-id',None) is None:
                    print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
                    req.headers['x-container-sysmeta-owner'] = userid
                elif new_resp.headers.get('x-container-sysmeta-owner',None) != userid:
                    print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
                    return HTTPUnauthorized(body="Unauthorized")(env, start_response)
        if req.method == "GET" and username != "ceilometer" and username != "admin" and username != None:
            if obj != None:
                new_req = Request.blank(req.path_info,None,req.headers,None)
                new_req.method = "HEAD"
                new_req.path_info = "/".join(["",version,account,container])
                response = new_req.get_response(self.app)
                cont_header = response.headers
                container_sel_id = cont_header.get('x-container-meta-sel-id',None)
                if container_sel_id is not None:
                    resp_obj = req.get_response(self.app)
                    object_sel_id = resp_obj.headers.get('x-object-meta-sel-id',None)
                    if object_sel_id != container_sel_id:
                        dek = get_cat_node(self.userID,container_sel_id).get('KEK',None)
                        if dek is not None:
                            env['swift_crypto_fetch_key'] = dek
                        else:
                            env['swift_crypto_fetch_key'] = "NotAuthorized"
        return self.app(env, start_response)

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
