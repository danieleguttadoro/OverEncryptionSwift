import json
import base64
from itertools import *
from crypto_functions import *
from connection import *
from swiftclient import client


meta_conn_sel = client.Connection(user=USER, key=KEY, tenant_name=META_TENANT_SEL,
                              authurl=AUTHURL, auth_version='2.0')

def get_catalog_sel(userID):
    """
    Get the catalog from the meta-container
    """
    CatContainer = '.Cat_usr%s' % userID
    CatSource = '$cat_graph%s.json' % userID
    try:
        hdrs, json_data_catalog = meta_conn_sel.get_object(CatContainer, CatSource)
    except:
        json_data_catalog = '{err}'
    return json_data_catalog


def load_graph_sel(usrID):
    """
    Load the graph from the catalog.
    This function differs from 'get_graph' because there are no information
    on nodes father (i.e. keys NODE and ACL)
    Args:
        usrID: the ID of the user
    Returns:
        The graph as a list of nodes (a list of dictionaries)
    """
    catalog = get_catalog_sel(usrID)
    json_cat = json.loads(catalog)
    return json_cat['NODES']


def get_DerivPath(userID, graph, destination):
    """
    Args:
        graph: the graph seen by the user
        destination: the ACL of the destination node
    Returns:
        the path from the root to the destination node
    """
    source = userID
    pathInv = []
    # Build a path bottom-up
    currDestination = destination
    currSource = None
    while currSource != source:
        for entry in [elem for elem in graph if elem['ACL_CHILD'] == currDestination]:
            currSource = entry['ACL']
            currDestination = entry['ACL']
            if tokenIsValid(entry['CRYPTOTOKEN'], entry['OWNERTOKEN']):
                pathInv.append(entry)

    # Invert the path built in the previous step to make it browsable
    return pathInv[::-1]


def majorChild(graph, new_node_Acl):
    """
    Get the parent node of the new node (it may be a child node itself)
    Args:
        graph: the graph seen by the user
        new_node_Acl: the ACL of the new node
    Returns:
        majChl: the parent node
        majChlACL: the parent node's ACL
    """
    majChl = None
    majChlACL = None
    majChlDim = None
    for node in graph:
        # If there are elements in discard list, this node cannot be parent of the new node
        discard = filter(lambda x: x not in new_node_Acl.split(':'), node['ACL_CHILD'].split(':'))
        if not discard:
            if len(node['ACL_CHILD'].split(':')) >= majChlDim:
                majChlDim = len(node['ACL_CHILD'].split(':'))
                majChl = node['NODE_CHILD']
                majChlACL = node['ACL_CHILD']
    return majChl, majChlACL


def browsePath(userID, MyPath):
    """
    Browse a path and derive the token.
    Returns:
        k: the decrypted message
        lastOwnerToken: who generated the token
    """
    k = None
    for step in MyPath:
        if not k:
            # First arch (or single arch)
            k = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
                              sender=step['OWNERTOKEN'], receiver=userID)
            k_prec = k
        else:
            token_ciph = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
                                       sender=step['OWNERTOKEN'], receiver=userID)
            k = decrypt_msg(base64.b64decode(token_ciph), k_prec)
            k_prec = k
        lastOwnerToken = step['OWNERTOKEN']
    return k, lastOwnerToken


def tokenIsValid(token, owner):
    """
    Control the validity of a token. Left for future implementation.
    Returns:
        True if the token is valid, false otherwise
    """
    return True

def get_token_sel(userID, acl_list):
    """
    """
    return "0123456789012345"

    eiteral_Acl_share_sorted = ':'.join(sorted(acl_list))
    myPath = []
    myPath = get_DerivPath(userID, get_graph(get_catalog_sel(userID)), literal_Acl_share_sorted)
    if len(myPath) == 0:
        return None, None
    token, lastOwnerToken = browsePath(userID, myPath)
    return token
