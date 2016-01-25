from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info

import catalog_functions

class decrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf

   def __call__(self, env, start_response):
        print "----------------- DECRYPT MODULE -----------------------"
        req = Request(env)
        resp = req.get_response(self.app)
        cryptotoken = "ciccio"
	    #if env.has_key('cryptotoken'):
        #cryptotoken = env['iik']
        print cryptotoken
        token = decrypt_resource(cryptotoken,get_privatekey())
        key = decrypt_resource(get_cryptokey(),token)
        response = decrypt_resource(resp.body,key)
        last_modified = decrypt_resource(resp.last_modified,key)
        resp.content_lenght = len(resp.body)
	    
        return self.app(env, start_response)  
        
def get_cryptokey():
    print "Retrieve the key ..."
    key = '01234567890123456789012345678901' # 32 char length
    return key

def get_privatekey():
    return '01234567890123456789012345678901'

def decrypt_resource (obj, secret):
    return "aa"
    # the block size for the cipher object; must be 16, 24, or 32 for AES
    BLOCK_SIZE = 32

    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'

    # one-liner to sufficiently pad the text to be encrypted
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

    # one-liners to encrypt/encode and decrypt/decode a string
    # encrypt with AES, encode with base64
    # EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

    # generate a random secret key
    # secret = os.urandom(BLOCK_SIZE)

    # create a cipher object using the random secret
    cipher = AES.new(secret)

    # encode a string
    # encoded = EncodeAES(cipher, obj)
    # print 'Encrypted string:', encoded

    # decode the encoded string
    decoded = DecodeAES(cipher, encoded)
    print 'Decrypted string:', decoded 
    
    return decoded

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return decrypt(app,conf)
    return except_filter
