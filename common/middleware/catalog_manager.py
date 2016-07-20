#!/usr/bin/env python

import json
import base64
from itertools import *
from key_manager import *
from keystoneauth1.identity import v2
from keystoneclient import session
from barbicanclient import client as bc
from connection import *

def get_secret(iduser,container_ref,idkey,tenant_name):
    auth = v2.Password(username=SWIFT_USER,password=SWIFT_PASS,auth_url=AUTH_URL,tenant_name=tenant_name)
    sess = session.Session(auth=auth)
    barbican = bc.Client(session=sess)
    container = barbican.containers.get(container_ref)
    idkey = str(idkey) + str(iduser)
    #container.secrets contains all the references to secrets
    for sec in container.secrets.keys():
        if sec == idkey:
            secret_node = barbican.secrets.get(container.secrets[sec].secret_ref)
            secret_node = json.loads(secret_node.payload)
            node = secret_node.copy()
            if node:
                dek = decrypt_KEK(secret=base64.b64decode('%s' % node['KEK']),signature=base64.b64decode('%s' % node['SIGNATURE']), sender=node['OWNERID'],receiver=iduser)
                node['KEK'] = dek
                return node

def get_catalog (iduser):
    """
    Get the catalog from the meta-container
    Args:
        iduser: The user id 
    Returns:
        json_data_catalog: User catalog (json format)
    """
    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        hdrs, json_data_catalog = meta_conn.get_object(CatContainer, CatSource)
    except: 
        json_data_catalog = '{}'
    return json_data_catalog

def load_catalog(iduser):
    """
    Load the catalog (json format) into the cat variable
    Args:
        iduser: The user id
    Returns:
        cat: The user catalog in json format 
    """
    cat = get_catalog(iduser)
    return json.loads(cat)

def get_cat_node (iduser,idkey):
    """
    Load the catalog and get a node with idkey from it
    Args:
        iduser: The user id
        idkey: The KEK id
    Returns:
        node: The stored node, with the correspondent DEK
    """
    cat = load_catalog(iduser)
    return get_node(cat,iduser,idkey)

def get_node(cat,iduser,idkey):
    """
    Get a node with idkey from the user catalog
    Args:
        cat: The user catalog
        iduser: The user id
        idkey: The KEK id
    Returns:
        node: The stored node, with the correspondent DEK
    """
    node = cat.get(idkey,{})
    if node:
        dek = decrypt_KEK(secret=base64.b64decode('%s' % node['KEK']),
                          signature=base64.b64decode('%s' % node['SIGNATURE']),
                          sender=node['OWNERID'],receiver=iduser)
        node['KEK'] = dek
    return node # return a clear node
