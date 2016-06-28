#!/usr/bin/env python

import json,os,base64
from itertools import *

from swiftclient import client
from middleware.connection import *

from myLogger import *

meta_conn = client.Connection(user=ADMIN_USER, key=ADMIN_KEY, tenant_name=META_TENANT,
                              authurl=AUTH_URL, auth_version='2.0')

def create_catalog(usrID, daemonID):
    """
    Generate a personal container .Cat_usr<UserID>
    and an empty catalog $cat_graph<UserID>.json
    Args:
        usrID: user's Keystone ID
        daemonID: admin daemon's ID
    """
    CatContainer = '.Cat_usr%s' % usrID
    CatSource = '$cat_graph%s.json' % usrID

    # Create meta-container
    try:
        meta_conn.put_container(CatContainer, headers=None)
        logging.debug("Meta-container %s put" % CatContainer)
    except:
        logger.debug('Error while putting the meta-container %s' % CatContainer)
        
    # Add ACL for this user to the meta-container
    cntr_headers = {}
    cntr_headers['x-container-read'] = ','.join([str(usrID),str(daemonID)])
    cntr_headers['x-container-write']= daemonID
    try:
        meta_conn.post_container(CatContainer, headers=cntr_headers)
        logger.debug("Header for meta-container %s set" % CatContainer)
    except:
        logger.debug('Error while setting the meta-container %s header' % CatContainer)

    # Create catalog       
    try:
        meta_conn.put_object(CatContainer, CatSource, json.dumps({}, indent=4, sort_keys=True), content_type='application/json')
        logger.debug("Catalog %s put in meta-container" % CatSource)
    except:
        logger.debug('Error while putting the catalog %s' % CatSource)

    return

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
        logger.debug("Error while getting catalog %s in meta-container" % CatSource)
        json_data_catalog = '{}'
    return json_data_catalog

def put_catalog (iduser, cat): #create_catalog == put_catalog (iduser, {})
    """
    Upload the catalog into the meta-container
    Args: 
        iduser: The user id
        cat: User catalog stored in the meta-container
    """
    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        meta_conn.put_object(CatContainer, CatSource, cat)
        return True
    except:
        logger.debug('Error while putting the catalog %s' % CatSource)

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

def update_catalog (iduser, idkey, obj):
    """
    Add a new KEK (obj) into the catalog
    Upload the new version catalog
    Args:
        iduser: The user id
        idkey: The DEK id
        obj: The new KEK
    """
    hash_map = load_catalog(iduser)
    
    if obj:
        hash_map[idkey] = obj
    else: 
        del hash_map[idkey]

    put_catalog(iduser, json.dumps(hash_map, indent=4, sort_keys=True))

