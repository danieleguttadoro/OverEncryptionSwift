from swift import gettext_ as _

from swift.common.swob import Request, Response, HTTPServerError
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext


from bz2 import BZ2Compressor
from itertools import chain, ifilter


import os, random, struct
from Crypto.Cipher import AES

import base64

from swift.proxy.controllers.base import get_container_info
from swift.proxy.controllers.base import get_account_info

import time
import hashlib

from swift.common.http import is_success
from swift.common.swob import wsgify

class key_master(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   @wsgify
   def __call__(self, req):
        print "-----------------OVERENCRYPT -----------------------"
        #req = Request(env)
        #username = env.get('HTTP_X_USER_NAME',None)
        #userid = env.get('HTTP_X_USER_ID', None)
	""" 
        for a in env.keys():
            print "---------------NEXT KEY------------------" + a 
            print env[a]
            if a=='HTTP_X_USER_NAME':
                print "USERNAME ----> " + env['HTTP_X_USER_NAME']
                break
            if a=='HTTP_X_USER_ID':
                print "USERID ----> " + env['HTTP_X_USER_ID']
                continue
        print username
        print env
       """
        resp = req.get_response(self.app)

        if is_success(resp.status_int) and req.method == 'GET':
         #   version, account, container, obj = req.split_path(1, 4, True)
          #  if not obj:
                # request path had no object component -- account or container PUT
           #     return self.app(env, start_response)
 
        # We're doing an object PUT -- wrap the input stream
        # Make sure to avoid reading everything into memory
        #not_blank = lambda somestr: somestr != ''

        #bz = BZ2Compressor()
        #compressed = chain((bz.compress(i) for i in env['wsgi.input']),
        #(bz.flush() for i in (1,)))
        #env['wsgi.input'] = ifilter(not_blank, compressed)
        #print "account info ..........................."
        #print get_account_info(req.environ, self.app)
        #print "container info ............................"
        #print get_container_info(req.environ, self.app)
            print "resp content_length ..........................."
            print resp.content_length
            #time.sleep(3)
	    print "resp  type ..........................."
            print resp.content_type
            #time.sleep(3)
            print "resp range ..........................."
            print resp.content_range
            #time.sleep(3)
            print "resp etag ..........................."
            print resp.etag
            #time.sleep(3)
            print "resp status ..........................."
            print resp.status
            #time.sleep(3)
            print "resp body ..........................."
            print resp.body
            #time.sleep(3)
            print "resp host_url ..........................."
            print resp.host_url
            #time.sleep(3)
            print "resp last_modified ..........................."
            print resp.last_modified
            #time.sleep(3)
            print "resp location ..........................."
            print resp.location
            #time.sleep(3)
            print "resp accept_ranges ..........................."
            print resp.accept_ranges
            #time.sleep(3)
            print "resp charset ..........................."
            print resp.charset
            #time.sleep(3)
            print "resp app_iter ..........................."
            print resp.app_iter
            #time.sleep(3)

	    
            resp.body = encrypt_file(resp.body)
            x = 0;
            for c in encrypt_file(str(resp.content_length)): 
		x += ord(c)

    	    resp.content_length = 125   #crea una lambda function per calcolare x
	    #resp.content_type = encrypt_file(str(resp.content_type))
	    #resp.last_modified = encrypt_file(str(resp.last_modified))

	    return resp

        #return self.app(env, start_response)

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
        acc_name = 'AUTH_' + second[0]
        collect = first[0] + '_' + second[0] + '/meta'] 
        print 'collect' + collect
        env2 = env
        env2['PATH_INFO'] = collect
        print env.keys()
        req2 = Request(env2)
 
        cl_get = ContainerController(self.app,acc_name,'meta')
        cl_get.GET(req2) """
 

def encrypt_file (obj):
    """ Encrypts a file using AES (CBC mode) with the
        given key.
        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.
        in_filename:
            Name of the input file
        out_filename:
            If None, '<in_filename>.enc' will be used.
        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
   
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))"""

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
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

    # generate a random secret key
    secret = os.urandom(BLOCK_SIZE)

    # create a cipher object using the random secret
    cipher = AES.new(secret)

    # encode a string
    encoded = EncodeAES(cipher, obj)
    print 'Encrypted string:', encoded

    # decode the encoded string
    #decoded = DecodeAES(cipher, encoded)
    #print 'Decrypted string:', decoded 
    return encoded

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return key_master(app,conf)
    return except_filter
