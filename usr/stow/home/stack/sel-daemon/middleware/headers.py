from flask.wrappers import Request
from keystoneclient import exceptions
from werkzeug.exceptions import Unauthorized

class HeaderGetter(object):
    """Header Getter middleware"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ, shallow=True)
        auth = req.headers.get('X-Auth-Token')
        path = environ.get('PATH_INFO','')
        if path not in ('/create'):
            try:
                get_raw_token_from_identity_service(auth_url=AUTH_URL,
                                                    token=auth)
            except exceptions.AuthorizationFailure:
                return Unauthorized()(environ, start_response)
        return self.app(environ, start_response)
