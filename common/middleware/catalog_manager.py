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
    except Exception, err: 
        print Exception,err
        json_data_catalog = '{err}'
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

"""    def create_node (self, iduser, idcontainer):
        '''
        Create a new node to put into the user catalog.
        The node includes the KEK, the owner id and the container id
        Args:
            iduser: The user id
            idcontainer: The container id
        Returns:
            idkey: the KEK id
            obj: the created node
        '''
        DEK_id, dek = self.key_manager.generate_container_key()
        obj = {}
        obj['KEK'] = base64.b64encode(dek)
        obj['IDCONTAINER'] = idcontainer
        obj['OWNERID'] = iduser
        return DEK_id, obj # clear dek in obj
        
    def put_catalog (self, iduser, cat): #create_catalogue == put_catalogue (iduser, {})
        '''
        Upload the catalog into the meta-container
        
        Args: 
            iduser: The user id
            cat: User catalog stored in the meta-container
        Returns:
            
        '''
        CatContainer = '.Cat_usr%s' % iduser
        CatSource = '$cat_graph%s.json' % iduser
        try:
            self.key_manager.meta_conn.put_object(CatContainer, CatSource, cat)
            return True
        except Exception, err:
            logger.debug(Exception, err)           
    def update_catalog (self, iduser, idkey, obj):

        hash_map = self.load_catalog(iduser)
        
        if obj:
            hash_map[idkey] = obj
        else: 
            del hash_map[idkey]

        put_catalog(iduser, json.dumps(hash_map, indent=4, sort_keys=True))
    
    def get_cat_crypto_node (iduser, idkey):
    
        hash_map = load_catalog(iduser)
        return hash_map.get(idkey,{})
"""
