mport json
import base64
from itertools import *
from crypto_functions import *
from connection import *
from swiftclient import client

meta_conn_sel = client.Connection(user=ADMIN_USER, key=ADMIN_KEY, tenant_name=META_TENANT_SEL,
                              authurl=AUTHURL, auth_version='2.0')

def get_catalogue (iduser):

    """
    Get the catalog from the meta-container
    """
    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        hdrs, json_data_catalog = meta_conn_sel.get_object(CatContainer, CatSource)
    except Exception, err: 
        print Exception, err
        json_data_catalog = '{err}'
    return json_data_catalog

def put_catalogue (iduser, cat): #create_catalogue == put_catalogue (iduser, {})

    CatContainer = '.Cat_usr%s' % iduser
    CatSource = '$cat_graph%s.json' % iduser
    try:
        meta_conn_sel.put_object(CatContainer, CatSource, cat)
        return True
    except Exception, err:
        print Exception, err           

def load_catalogue(iduser)

    cat = get_catalogue(iduser)
    return json.loads(cat)

def update_catalogue (iduser, idkey, obj):

    hash_map = load_catalogue(iduser)
    hash_map[idkey] = obj
    put_catalogue(iduser, hash_map)

def get_cat_crypto_node (iduser, idkey):

    hash_map = load_catalogue(iduser)
    return hash_map[idkey]

def get_cat_token (iduser, idkey):

    crypto_node = get_cat_crypto_node(iduser,idkey)
    key = get_key()
    token = decrypt_token(crypto_node['TOKEN'],key)
    return token

def create_node (iduser, idcontainer):

    idkey, token = gen_token()
    obj = {}
    obj['TOKEN'] = token 
    obj['IDCONTAINER'] = idcontainer
    obj['OWNERTOKEN'] = iduser
    return idkey, obj # clear token in obj

