import os
import binascii
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import codecs
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

def get_privatekey():
    return '01234567890123456789012345678901'

def gen_token():
     
    # generate a random secret token
    random_byte = os.urandom(BLOCK_SIZE/2) 
    token_ascii = binascii.hexlify(random_byte)
    print len(token_ascii)
    return token_ascii
    
def gen_key():
    
    # generate a random secret token
    random_byte = os.urandom(BLOCK_SIZE/2) 
    token_ascii = binascii.hexlify(random_byte)
    print len(token_ascii)
    return token_ascii


def decrypt_resource (obj, secret):
    
    # create a cipher object using the secret
    cipher = AES.new(secret)

    # decode the encoded string
    decoded = DecodeAES(cipher, obj)
    #print 'Decrypted string:', decoded 
    
    return decoded

def encrypt_resource(obj,secret):
    
    # create a cipher object using the secret
    cipher = AES.new(secret)
    
    # encode a string
    encoded = EncodeAES(cipher, obj)
    #print 'Encrypted string:', encoded

    return encoded
