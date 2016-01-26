import os
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

def get_key():
    return "key"

def get_cryptokey():
    print "Retrieve_the_key"
    key = '01234567890123456789012345678901' # 32 char length
    return key

def get_privatekey():
    return '01234567890123456789012345678901'

def gen_token():
    return "token"

def encrypt(key,content):
    return content

def decrypt_resource (obj, secret):
    return obj
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


