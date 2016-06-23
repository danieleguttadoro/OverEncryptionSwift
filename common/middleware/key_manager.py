#!/usr/bin/env python

import os
import base64
from Crypto import Random
from Crypto.Cipher import AES,PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
#from Crypto.PublicKey import RSA
import imp
from connection import *
from swiftclient import client

RSA = imp.load_source('Crypto.PublicKey', '/usr/lib/python2.7/dist-packages/Crypto/PublicKey/RSA.py')

meta_conn = client.Connection(user=SWIFT_USER, key=SWIFT_PASS, tenant_name=META_TENANT,
                                       authurl=AUTH_URL, auth_version='2.0')

BLOCK_SIZE = 16

def generate_container_key():
    """
    Generate a random AES key for the container
    """
    random_bytes = os.urandom(BLOCK_SIZE)
    secret = base64.b64encode(random_bytes).decode('utf-8')
    id_ = uuid.uuid4()

    return id_,secret

def decrypt_KEK(secret,signature, sender, receiver):
        """
        Decipher the KEK from the catalog.
        
        Returns:
            Dek
        """
        sender_pub_key = RSA.importKey(get_publicKey(sender))
        # receiver = self.userID
        if sender == receiver:
            # AES decipher
            h = SHA256.new()
            h.update(secret)
            verifier = PKCS1_PSS.new(sender_pub_key)
            if verifier.verify(h,signature):
                master_key = get_masterKey()
                unpad = lambda s: s[: -ord(s[len(s) - 1:])]
                secret = base64.b64decode(secret)
                iv = secret[:BLOCK_SIZE]
                cipher = AES.new(master_key, AES.MODE_CBC, iv)
                result = unpad(cipher.decrypt(secret[BLOCK_SIZE:]))
            else:
                #error
                pass
        else:
            # RSA decipher
            receiver_priv_key_rsa = RSA.importKey(get_privateKey())
            receiver_priv_key = PKCS1_OAEP.new(receiver_priv_key_rsa)
            h = SHA256.new()
            h.update(secret)
            verifier = PKCS1_PSS.new(sender_pub_key)
            if verifier.verify(h,signature):
                result = receiver_priv_key.decrypt(secret)
                return result
            else:
                pass
                #error
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

def get_masterKey():    
    """ 
    Get the user's master key
    Returns:
        The master key
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

def get_publicKey(usrID):    # TODO: from barbican
    """
    Get the user's public key
    Returns:
        Public key from meta-container (Keys) in meta-tenant
    """
    filename =  usrID
    try:
        hdrs, obj = meta_conn.get_object("Keys", filename)
    except:
        return
    return obj
