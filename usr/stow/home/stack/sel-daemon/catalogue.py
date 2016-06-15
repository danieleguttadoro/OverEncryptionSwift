#!/usr/bin/env python

import json
import base64
from itertools import *

from swiftclient import client
from connection import *
meta_conn = client.Connection(user=ADMIN_USER, key=ADMIN_KEY, tenant_name=META_TENANT,
                              authurl=AUTH_URL, auth_version='2.0')

def create_catalog(self, usrID, daemonID, force=False):
        """
        Generate a personal container .Cat_usr<UserID>
        and an empty catalog $cat_graph<UserID>.json
        Args:
            usrID: user's Keystone ID
            PARAM 'force': force the creation of new keys and reset the catalog
        """
        CatContainer = '.Cat_usr%s' % usrID
        CatSource = '$cat_graph%s.json' % usrID

        if not force:
            if os.path.exists(CatSource):
                cu_logger.error("ENV_ERR User_props already exists")
                return
        
        # Create meta-container
        try:
            meta_conn.put_container(CatContainer, headers=None)
            #cu_logger.info("Meta-container %s put" % CatContainer)
        except:
            pass
            #cu_logger.error('Error while putting the meta-container %s' % CatContainer)
        
        # Add ACL for this user to the meta-container
        cntr_headers = {}
        cntr_headers['x-container-read'] = ','.join([usrID,daemonID])
        cntr_headers['x-container-write']= ','.join([usrID,daemonID,])
        try:
            meta_conn.post_container(CatContainer, headers=cntr_headers)
            #cu_logger.info("Header for meta-container %s set" % CatContainer)
        except:
            pass
            #cu_logger.error('Error while setting the meta-container %s header' % CatContainer)

        # Create catalog       
        try:
            meta_conn.put_object(CatContainer, CatSource, json.dumps({}, indent=4, sort_keys=True), content_type='application/json')
            #cu_logger.info("Catalog %s put in meta-container" % CatSource)
        except:
            pass
            #cu_logger.error('Error while putting the catalog %s' % CatSource)

        # Post header Label via STD post_object
        obj_headers = {}
        obj_headers['x-container-read'] =  ','.join([usrID,daemonID])
        obj_headers['x-container-write']=  ','.join([usrID,daemonID])
        try:
            meta_conn.post_object(CatContainer, CatSource, headers=obj_headers)
            #cu_logger.info("Header for catalog %s set" % CatSource)
        except:
            pass
            #cu_logger.error('Error setting catalog %s header' % CatSource)

        #cu_logger.info("Generated and Stored personal catalog.")
        return


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

    put_catalogue(iduser, json.dumps(hash_map, indent=4, sort_keys=True))

def get_cat_crypto_node (iduser, idkey):

    hash_map = load_catalogue(iduser)
    return hash_map.get(idkey,{})
'''
def get_cat_obj (iduser,idkey):

    node = get_cat_crypto_node(iduser,idkey)
    if node:
        token = decrypt_token(secret=base64.b64decode('%s' % node['TOKEN']),
                              sender=node['OWNERTOKEN'],receiver=iduser)
        node['TOKEN'] = token
    return node # return a clear node
'''
def create_node (iduser, idcontainer):

    idkey, token = generate_container_key()
    obj = {}
    obj['TOKEN'] = base64.b64encode(token)
    obj['IDCONTAINER'] = idcontainer
    obj['OWNERTOKEN'] = iduser
    return idkey, obj # clear token in obj

