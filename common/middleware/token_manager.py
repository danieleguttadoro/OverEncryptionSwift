#!/usr/bin/env python

import os
import base64
from Crypto import Random
from Crypto.Cipher import AES
#from Crypto.PublicKey import RSA
import imp
from connection import *
from swiftclient import client

meta_conn = client.Connection(user=ADMIN_USER, key=ADMIN_KEY, tenant_name=META_TENANT,
                              authurl=AUTH_URL, auth_version='2.0')

RSA = imp.load_source('Crypto.PublicKey', '/usr/lib/python2.7/dist-packages/Crypto/PublicKey/RSA.py')

BLOCK_SIZE = 16

def generate_container_key():
    """
    Generate a random AES key for the container
    """
    random_bytes = os.urandom(BLOCK_SIZE)
    secret = base64.b64encode(random_bytes).decode('utf-8')

    random_id = os.urandom(BLOCK_SIZE/4)
    id_ = base64.b64encode(random_id).decode('utf-8')
    return id_,secret


def encrypt_token(secret, sender, receiver):
    """
    Cipher the token for the catalog using either AES or RSA encryption
    """
    # sender = self.userID
    if sender == receiver:
        # AES encryption using the master key
        master_key = get_masterKey()
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        secret = pad(secret)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = base64.b64encode(iv + cipher.encrypt(secret))
    else:
        # RSA encryption using the sender's private key and the receiver's public one
        sender_priv_key = RSA.importKey(get_privateKey())
        receiver_pub_key = RSA.importKey(get_publicKey(receiver))
        ciph1 = sender_priv_key.decrypt(secret)
        result = receiver_pub_key.encrypt(ciph1, 'x')[0]
    return result


def decrypt_token(secret, sender, receiver):
    """
    Decipher the token from the catalog.
    Returns:
        The plain token
    """
    # receiver = self.userID
    if sender == receiver:
        # AES decipher
        master_key = get_masterKey()
        unpad = lambda s: s[: -ord(s[len(s) - 1:])]
        secret = base64.b64decode(secret)
        iv = secret[:BLOCK_SIZE]
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = unpad(cipher.decrypt(secret[BLOCK_SIZE:]))
    else:
        # RSA decipher
        sender_pub_key = RSA.importKey(get_publicKey(sender))
        receiver_priv_key = RSA.importKey(get_privateKey())
        deciph1 = receiver_priv_key.decrypt(secret)
        result = sender_pub_key.encrypt(deciph1, 'x')[0]
    return result


def encrypt_msg(info, secret, path=False):
    """
    Encrypt a message using AES
    """
    print info
    print secret
    print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    # padding : guarantee that the value is always MULTIPLE  of BLOCK_SIZE
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    encodeAES = lambda c, s: (c.encrypt(pad(s)))
    cipher = AES.new(secret)
    encoded = encodeAES(cipher, info)
    if path:
        # Encoding base32 to avoid paths (names containing slashes /)
        encoded = (encoded)
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

def get_masterKey():    
    """ 
    Get the user's public key
    Returns:
        Public key
    """

    filename = '/opt/stack/swift/swift/common/middleware/mk.key'
    with open(filename, 'r') as f:
        master_key = f.read()
    return base64.b64decode(master_key)
    
def get_privateKey():  
    """
    Get the plain user's private key
    Returns:
        The plain private key
    """
    filename = '/opt/stack/swift/swift/common/middleware/pvt.key'
    with open(filename, 'r') as f:
        private_key = f.read()
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    private_key = base64.b64decode(private_key)
    iv = private_key[:BLOCK_SIZE]
    cipher = AES.new(get_masterKey(), AES.MODE_CBC, iv) 
    return unpad(cipher.decrypt(private_key[BLOCK_SIZE:]))

def get_publicKey(userID):    # TODO: from barbican
    """
    Get the user's public key
    Returns:
        Public key from barbican
    """
    filename =  userID
    try:

        hdrs, obj = meta_conn.get_object("Keys", filename)
    except Exception,err:
        print Exception, err
        print ("Error in retrieve RSA public key.")
        return
    return obj

