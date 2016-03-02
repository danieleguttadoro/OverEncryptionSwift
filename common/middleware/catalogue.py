#!/usr/bin/env python

import json
import base64
from itertools import *
from crypto_functions import *

def get_catalogue (iduser):

    """
    Get the catalog from the meta-container
    """
    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        hdrs, json_data_catalog = meta_conn.get_object(CatContainer, CatSource)
    except Exception, err: 
        print Exception, err
        json_data_catalog = '{err}'
    return json_data_catalog

def put_catalogue (iduser, cat): #create_catalogue == put_catalogue (iduser, {})

    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        meta_conn.put_object(CatContainer, CatSource, cat)
        return True
    except Exception, err:
        print Exception, err           

def load_catalogue(iduser):

    cat = get_catalogue(iduser)
    return json.loads(cat)

def update_catalogue (iduser, idkey, obj):

    hash_map = load_catalogue(iduser)
    
    if obj:
        hash_map[idkey] = obj
    else: 
        del hash_map[idkey]

    put_catalogue(iduser, json.dumps(hash_map))

def get_cat_crypto_node (iduser, idkey):

    hash_map = load_catalogue(iduser)
    return hash_map[idkey]

def get_cat_obj (iduser,idkey):

    node = get_cat_crypto_node(iduser,idkey)
    token = decrypt_token(secret=base64.b64decode('%s' % node['TOKEN']),
                          sender=node['OWNERTOKEN'],receiver=iduser)
    node['TOKEN'] = token
    return node # return a clear node

def create_node (iduser, idcontainer):

    idkey, token = generate_container_key()
    obj = {}
    obj['TOKEN'] = base64.b64encode(token)
    obj['IDCONTAINER'] = idcontainer
    obj['OWNERTOKEN'] = iduser
    return idkey, obj # clear token in obj
