from swift import gettext_ as _

from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext

from swift.common.swob import wsgify

class key_master(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   
   def __call__(self, env, stat_response):
        print "----------------- KEY_MASTER -----------------------"
        
        req = Request(env)
        resp = req.get_response(self.app)

        # retrieve the key 
        print "retrieve the key ..."
        key = '01234567890123456789012345678901' # 32 char length

        if key == '':
            raise_error(req,403)

        env['swift_crypto_fetch_crypto_key'] = key

        return self.app(env, start_response)

@wsgify
def raise_error(req,stat):

    if stat == 403:
        return Response(request=req, status=403, body="USER UNAUTHORIZED TO OBTAIN THIS FILE",
                        content_type="text/plain")


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
