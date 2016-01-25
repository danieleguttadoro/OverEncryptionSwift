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
def add_node(graph,Entry,parent,userid):
    # New node
    Parent = [elem for elem in graph if elem.has_key('NODE') and elem['NODE'] == parent ]
    if len(Parent) == 0:
        # No token exiting from current node exist, also the parent node must be created
        CatGrEntry = {}
        CatGrEntry["NODE"] = parent
        CatGrEntry["ACL"] = parent
        CatDtEntryList = []
        CatDtEntryList.append(Entry)
        CatGrEntry["TOKEN"] = CatDtEntryList
        graph['NODES']=CatGrEntry
    else:
	    # The source node already exists. Only the destination+token must be appended
        for elem in [elem for elem in graph if elem['NODE'] == parent]:
            Parent[0]['TOKEN'].append(Entry)

    NewEntry = {}
    NewEntry["TYPE_ENTITY"] = "USER"
    NewEntry["ID_ENTITITY"] = userid
    NewEntry["NODES"] = graph
    EntryWrite = NewEntry
    return json.dumps(EntryWrite, indent=4, sort_keys=True)

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
	        pass
            #child['NODE'] = x['NODE']
            #child['ACL'] = x['ACL']
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
        graph: the graph seen by the user (obtained by load_graph)
        container
    Returns:
        the path from the root to the destination node
    """
	
    currDestination = destination
    for elem in graph:
       if elem.has_key('TOKEN'):
         entry = elem['TOKEN']
         for ent in entry:	
          if currDestination == ent['NODE_CHILD']:
            if tokenIsValid(ent['CRYPTOTOKEN'], ent['OWNERTOKEN']):
               return ent
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

def remove_node(graph,container,userid):
    currContainer = container
    for elem in graph:
        if elem.has_key('TOKEN'):
            entry = elem['TOKEN']
            for ent in entry:
                if currContainer == ent['NODE_CHILD']:
                    entry.remove(ent)

    return graph

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
            # First arch (or single arch
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

def control_graph(catalog,container_list,userid):
     global graph
     graph = load_graph(catalog)
     for cont in container_list:
        graph = remove_node(graph,cont,userid)
        Entry = {}
        Entry["TYPE_ENTITY"] = "USER"
        Entry["ID_ENTITITY"] = userid
        Entry["NODES"] = graph
     return json.dumps(Entry, indent=4, sort_keys=True)
 

def new_cryptotoken(node):
    #TODO
    return "aaaaaaaa4"

def overencrypt(userid,catalog,container_list,acl_list):
    global graph
    graph = load_graph(catalog)
    new_acl_list = ':'.join(sorted(acl_list))
    for elem in container_list:
	    cryptotoken = new_cryptotoken(userid)
	    graph = remove_node(graph,elem,userid)
	    node = create_node(elem,new_acl_list,cryptotoken,userid)
	    graph = add_node(graph,node,userid,userid)
    return graph
