import os
import binascii
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import codecs
import time

#the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 16

def get_privatekey():
    return '01234567890123456789012345678901'

def gen_token():

    random_bytes = os.urandom(BLOCK_SIZE)
    secret = base64.b64encode(random_bytes).decode('utf-8')
    print "TOKEN"
    print secret
    print len(secret)
    time.sleep(3)
    return secret     
    
def gen_key():
    
    random_bytes = os.urandom(BLOCK_SIZE)
    secret = base64.b64encode(random_bytes).decode('utf-8')
    print "KEY"
    print secret
    print len(secret)
    time.sleep(3)
    return secret

def decrypt_resource (obj, secret):
    
    unpad = lambda s: s[: -ord(s[len(s) - 1:])]
    
    obj = base64.b64decode(obj)

    iv = obj[:BLOCK_SIZE]
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    
    result = unpad(cipher.decrypt(obj[BLOCK_SIZE:])) 
    
    return result

def encrypt_resource(obj,secret):

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    pad_obj = pad(obj)

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    result = base64.b64encode(iv + cipher.encrypt(pad_obj)) 

    return result


def encrypt_msg(info, secret, path=False):
    """
    Encrypt a message using AES
    """
    # padding : guarantee that the value is always MULTIPLE  of BLOCK_SIZE
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    encodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    cipher = AES.new(secret)
    encoded = encodeAES(cipher, info)
    if path:
        # Encoding base32 to avoid paths (names containing slashes /)
        encoded = base64.b32encode(encoded)
    return encoded


def decrypt_msg(encryptedString, secret, path=False):
    """
    Decrypt a message using AES
    """
    PADDING = '{'
    if path:
        encryptedString = base64.b32decode(encryptedString)
    decodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    key = secret
    cipher = AES.new(key)
    decoded = decodeAES(cipher, encryptedString)
    return decoded
