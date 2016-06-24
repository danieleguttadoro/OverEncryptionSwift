#!/usr/bin/env python

import json
import base64
from itertools import *
from key_manager import *

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
