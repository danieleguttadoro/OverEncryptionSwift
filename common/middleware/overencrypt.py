from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController

class overencrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf

   def __call__(self, env, start_response):
        print "-----------------OVERENCRYPT -----------------------"
        req = Request(env)
        username = env.get('HTTP_X_USER_NAME',None)
        userid = env.get('HTTP_X_USER_ID', None)
        print username

        #for a in env.keys():
        print "---------------KEYS------------------"
        print env.keys()
        print "---------------ENDKEYS---------------"
        print env['PATH_INFO']
        req_get= Request(env)
        #print req_get
        #cl_get = ContainerController(self.app,"admin","meta")
        #result = cl_get.GET(req_get)
        result = req_get.get_response(self.app)
        print result.status
        print "-------------------------RESULT-------------------------"
        #print result

        return self.app(env, start_response)       

"""        for a in env.keys():
                print "---------------NEXT KEY------------------" + a 
                print env[a]
		sleep(3)hhi
                if a=='HTTP_X_USER_NAME':
                        print "USERNAME ----> " + env['HTTP_X_USER_NAME']
                        break
                if a=='HTTP_X_USER_ID':
                        print "USERID ----> " + env['HTTP_X_USER_ID']
                        continue
        print env """

"""     GET METACONTAINER

        print "METHOD ----> " + req.method
        print "PATH REQUEST ---->" + req.path_info
        print username
        print userid
        print "ENV KEYS" + env['PATH_INFO']
        first = env['PATH_INFO'].split('_')
        print 'first'
        print first
        print 'second'
        second = first[1].split('/')
        print second
        second[1] = 'meta'
        acc_name = 'AUTH_' + second[0]
        collect = first[0] + '_' + second[0] + '/' + second[1] 
        print 'collect' + collect
        env2 = env
        env2['PATH_INFO'] = collect
        print env.keys()
        req2 = Request(env2)

        cl_get = ContainerController(self.app,acc_name,second[1])
        cl_get.GET(req2) """


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return overencrypt(app,conf)
    return except_filter
