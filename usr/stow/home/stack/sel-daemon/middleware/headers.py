from flask.wrappers import Request
from keystoneclient import exceptions
from keystoneclient.v2_0 import client as kc
from werkzeug.exceptions import Unauthorized
from connection import *

class HeaderGetter(object):
    """Header Getter middleware"""

    def __init__(self, app):
        self.app = app
        # Requires an admin connection
        self.kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_KEY, tenant_name=TENANT_NAME, auth_url=AUTH_URL)

    def __call__(self, environ, start_response):
        req = Request(environ, shallow=True)
        auth = req.headers.get('X-Auth-Token')
        path = environ.get('PATH_INFO','')
        if path not in ('/create'):
            try:
                print "try"
                self.kc_conn.get_raw_token_from_identity_service(auth_url=AUTH_URL,
                                                    token=auth)
            except exceptions.AuthorizationFailure:
                print "except"
                return Unauthorized()(environ, start_response)
            except Exception, err:
                print Exception, err
                return Unauthorized()(environ, start_response)
        return self.app(environ, start_response)
