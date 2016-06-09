#!/usr/bin/env python

import os
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from connection import *
from swiftclient import client

meta_conn = client.Connection(user=ADMIN_USER, key=ADMIN_KEY, tenant_name=META_TENANT,
                              authurl=AUTH_URL, auth_version='2.0')

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
        master_key = get_masterKey(sender)
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        secret = pad(secret)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = base64.b64encode(iv + cipher.encrypt(secret))
    else:
        # RSA encryption using the sender's private key and the receiver's public one
        sender_priv_key = RSA.importKey(get_privateKey(sender))
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
        master_key = get_masterKey(sender)
        unpad = lambda s: s[: -ord(s[len(s) - 1:])]
        secret = base64.b64decode(secret)
        iv = secret[:BLOCK_SIZE]
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = unpad(cipher.decrypt(secret[BLOCK_SIZE:]))
    else:
        # RSA decipher
        sender_pub_key = RSA.importKey(get_publicKey(sender))
        receiver_priv_key = RSA.importKey(get_privateKey(receiver))
        deciph1 = receiver_priv_key.decrypt(secret)
        result = sender_pub_key.encrypt(deciph1, 'x')[0]
    return result


def encrypt_msg(info, secret, path=False):
    """
    Encrypt a message using AES
    """
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
        encryptedString = (encryptedString)
    decodeAES = lambda c, e: c.decrypt((e)).rstrip(PADDING)
    key = secret
    cipher = AES.new(key)
    decoded = decodeAES(cipher, encryptedString)
    return decoded

def get_masterKey(userID):       # TODO: deprecate it
    """
    Get the master key from local file
    Returns:
        The master key
    """
    mk_filename = "mk_%s.key" % userID
    try:
        hdrs, obj = meta_conn.get_object("Keys", mk_filename)
    except:
        print ("Error in retrieve Master key.")
        return
    return base64.b64decode(obj)

def get_publicKey(userID):    # TODO: from barbican
    """
    Get the user's public key
    Returns:
        Public key from barbican
    """
    filename = 'pub_%s.key' % userID
    try:
        hdrs, obj = meta_conn.get_object("Keys", filename)
    except:
        print ("Error in retrieve RSA public key.")
        return
    return obj


def get_privateKey(userID):  # TODO: from barbican
    """
    Get the plain user's private key from barbican
    Returns:
        The plain private key
    """
    master_key = get_masterKey(userID)
    filename = 'pvt_%s.key' % userID
    try:
        hdrs, private_key = meta_conn.get_object("Keys", filename)
    except:
        print ("Error in retrieve RSA private key.")
        return
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    private_key = base64.b64decode(private_key)
    iv = private_key[:BLOCK_SIZE]
    cipher = AES.new(master_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(private_key[BLOCK_SIZE:]))


