from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info
class encrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf

   def __call__(self, env, start_response):
        print "-----------------ENCRYPT -----------------------"
        return self.app(env, start_response)  


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
