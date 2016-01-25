from swift import gettext_ as _

from swift.common.swob import Request, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext

import os, random, struct
from Crypto.Cipher import AES

import base64

from swift.common.http import is_success
from swift.common.swob import wsgify

class encrypt(WSGIContext):

    def __init__(self,app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        print "----------------- ENCRYPT -----------------------"
        

        req = Request(env)
        resp = req.get_response(self.app)
        
        if is_success(resp.status_int) and req.method == 'GET':
            pass
            #key = env['swift_crypto_fetch_crypto_key']
            #return encrypt_response(req,key,resp)


        return self.app(env, start_response)  

    @wsgify
    def encrypt_response (req,key,resp):

        resp.body = encrypt_resource(resp.body,key)
        
        x = 0 
        for c in encrypt_resource(str(resp.content_length),key): 
            x += ord(c)

        resp.content_length = x   #crea una lambda function per calcolare x
        resp.content_type = encrypt_resource(str(resp.content_type),key) #sembra un'istruzione inutile (linux riconosce che un file di testo)
        resp.last_modified = encrypt_resource(str(resp.last_modified),key) #sembra un'istruzione inutile (linux mette come ultima modifica la data di quando lo scarichi)
    
        return resp 
    
    def encrypt_resource (obj,secret):

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
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        # DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

        # generate a random secret key
        # secret = os.urandom(BLOCK_SIZE)

        # create a cipher object using the random secret
        cipher = AES.new(secret)

        # encode a string
        encoded = EncodeAES(cipher, obj)
        print 'Encrypted string:', encoded

        # decode the encoded string
        # decoded = DecodeAES(cipher, encoded)
        # print 'Decrypted string:', decoded 
    
        return encoded

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
