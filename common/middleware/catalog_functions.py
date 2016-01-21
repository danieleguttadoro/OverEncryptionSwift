#!/usr/bin/env python

import json
import base64
from itertools import *
from swift.common.swob import Request
#from crypto_functions import *

# Names of meta container and file of the graph
meta_container = "meta"
graph_tokens = "b"

#modified on server
def get_catalog(req,app):
    #COMMENT: Obtaining version and account of the Request, to do another Request and obtain the graph of tokens
    version, account, container, obj = req.split_path(1,4,True)
    path_meta = "/".join(["", version , account , meta_container, graph_tokens])
    print path_meta
    req_meta_container = Request.blank(path_meta,None,req.headers,None)
    catalog = req_meta_container.get_response(app)
    return req_meta_container, catalog.body

def create_node(node_child,acl_child,cryptotoken,ownertoken):
    Entry = {}
    Entry["NODE_CHILD"] = node_child
    Entry["ACL_CHILD"] = acl_child
    #TokenDecEscape = r"%s" % upd_details[7].decode('string-escape')
    Entry["CRYPTOTOKEN"] = cryptotoken# TokenDecEscape
    Entry["OWNERTOKEN"] = ownertoken
    #Entry["VERSIONTOKEN"] = '0'        # Left for future development
    #Entry["TYPE"] = 'USER'
    return Entry

#added in server
def add_node(graph,Entry):
    # New node
    Parent = [elem for elem in graph if elem['NODE'] == "8958ee5ec1b14ca5b19dcbc32bb45409"]

    if len(Parent) == 0:
            # No token exiting from current node exist, also the parent node must be created
            CatGrEntry = {}
            CatGrEntry["NODE"] = "newuser"
            CatGrEntry["ACL"] = "newuser"
            CatDtEntryList = []
            CatDtEntryList.append(Entry)
            CatGrEntry["TOKEN"] = CatDtEntryList
            graph.append(CatGrEntry)
    else:
	    # The source node already exists. Only the destination+token must be appended
            CatGrEntry = {}
            CatGrEntry["NODE"] = "Node"
            CatGrEntry["ACL"] = "newuser"
            for elem in [elem for elem in graph if elem['NODE'] == "8958ee5ec1b14ca5b19dcbc32bb45409"]:
                Parent[0]['TOKEN'].append(Entry)

    NewEntry = {}
    NewEntry["TYPE_ENTITY"] = "USER"
    NewEntry["ID_ENTITITY"] = "iduser"
    NewEntry["NODES"] = graph
    EntryWrite = NewEntry
    return json.dumps(EntryWrite, indent=4, sort_keys=True)
   
#added in server
def remove_node(graph):
    pass


def get_graph(json_data_catalog):
    """
    Read the catalog (simple version, without further browse) and build the graph.
    Args:
        json_data_catalog: the catalog .json
    Returns:
        CatGraph:
    """
    json_data = json.loads(json_data_catalog.decode('latin-1'), strict=False)
    CatGraph = []

    def foo(x):
        for child in x['TOKEN']:
            child['NODE'] = x['NODE']
            child['ACL'] = x['ACL']
        return x['TOKEN']

    CatGraph = map(foo, json_data['NODES'])
    CatGraph = list(chain.from_iterable(CatGraph))
    return CatGraph


def load_graph(json_data_catalog):
    """
    Load the graph from the catalog.
    This function differs from 'get_graph' because there are no information
    on nodes father (i.e. keys NODE and ACL)
    Args:
        usrID: the ID of the user
    Returns:
        The graph as a list of nodes (a list of dictionaries)
    """
    json_cat = json.loads(json_data_catalog)
    return json_cat['NODES']


#da modificare non == ma nella lista di container
def get_Node(graph, destination):
    """
    Args:
        graph: the graph seen by the user
        container
    Returns:
        the path from the root to the destination node
    """
    currDestination = destination
    for entry in [elem for elem in graph]:
       if currDestination == entry['NODE_CHILD']:
            if tokenIsValid(entry['CRYPTOTOKEN'], entry['OWNERTOKEN']):
               return entry
    return None

#NoT USED
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

#NOT USED
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
	    #PROVA
	    k = step['CRYPTOTOKEN']	
            #k = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
                              #sender=step['OWNERTOKEN'], receiver=userID)
            k_prec = k
        else:
	    token_ciph = step['CRYPTOTOKEN']
            #token_ciph = decrypt_token(secret=base64.b64decode('%s' % step['CRYPTOTOKEN']),
                                      # sender=step['OWNERTOKEN'], receiver=userIDi
            #k = decrypt_msg(base64.b64decode(token_ciph), k_prec)
            k = step['CRYPTOTOKEN']
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

def get_cryptotoken(catalog, container):
    myPath = get_Node(load_graph(catalog), container)
    if myPath == None:
        return None
    
    return myPath['CRYPTOTOKEN']

def new_cryptotoken(node):
    #TODO
    return "aaaaaaaa4"

def overencrypt(userid,catalog,container_list,acl_list):
    return None
    global graph
    graph = load_graph(catalog)
    new_acl_list = ':'.join(sorted(acl_list))
    for elem in container_list:
	node = get_Node(graph,elem)
	cryptotoken = new_cryptotoken(node)
	if node == None:
	    node = create_node(elem,new_acl_list,cryptotoken,userid)
	    #global graph
	    graph = add_node(graph,node)
	else:
	    cryptotoken = new_cryptotoken(node)
	    node = create_node(node["NODE_CHILD"],new_acl_list,cryptotoken,node["OWNERTOKEN"])
	    #global graph
	    graph = add_node(graph,node)

    return graph
