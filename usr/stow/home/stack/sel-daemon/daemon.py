#!/usr/bin/env python
from swift.common.middleware import catalog_functions as cf
from swift.common.middleware import crypto_functions as cr
import os, sys, psutil, time, pika
from multiprocessing import Process
#from keystoneclient.v3 import client
#from keystoneclient import session
#from keystoneclient.auth import base
#from swift.proxy import server
import swiftclient
from swiftclient.exceptions import ClientException as ce
from keystoneclient.v2_0 import client as kc
from keystoneclient.exceptions import NotFound,Conflict
import json
import signal

ADMIN_USER = 'admin'
ADMIN_PASS = 'secretsecret'
ADMIN_TENANT = 'admin'
AUTH_URL = 'http://localhost:5000/v2.0'


def new_cryptotoken(user,token):
    key = cr.get_privatekey()
    return cr.encrypt_resource(obj=token,secret=key)


def create_container(swift_conn,owner_cat):
 
    try:
        sel_tenant = kc_conn.tenants.find(name=owner_cat)
    except NotFound:
        sel_tenant = kc_conn.tenants.create(owner_cat,None)
    
    try:
        kc_conn.tenants.add_user(tenant=sel_tenant,user=UUID,role=admin_role)
    except Conflict:
       pass
    
    user_role = kc_conn.roles.find(name='Member')
    
    try:
        kc_conn.tenants.add_user(sel_tenant,owner_cat,user_role)
    except Conflict:
        pass
    
    try:
        swift_conn.put_container(owner_cat, headers=None)
    except:
        sys.stderr.write('Error while putting container %s' % owner_cat)

    # Add ACL for this container
    ACL_headers = {}
    ACL_headers['x-container-read'] = owner_cat
    ACL_headers['x-container-write'] = UUID
    ACL_headers['x-container-meta-acl_label'] = owner_cat+':'+UUID
        
    try:
        swift_conn.post_container(owner_cat, headers=ACL_headers)
    except:
        sys.stderr.write('Error while setting the %s ACL_headers' % owner_cat)

    return


def get_graph(swift_conn,user):

    try: 
        cat = swift_conn.get_object(container=user,obj=user)
    except ce:
        create_container(swift_conn,user) 
        return {}

    if cat[1] == '':
        return {} 
    
    return cf.load_graph(cat[1])
    
def insert_new_node(swift_conn,user,token,node,first_call_check):
    
    node['CRYPTOTOKEN'] = new_cryptotoken(user,token)
     
    graph = get_graph(swift_conn,user)
    acl_old = None
    if graph:
        if first_call_check:
            old_node = cf.get_node(graph,node['NODE_CHILD'])
            #Se non e' presente un nodo relativo al container, acl_old == None
            if old_node != None:
                acl_old = old_node['ACL_CHILD']
        #Se il nodo non e' presente nel grafo, restituisce il grafo intatto
        graph = cf.remove_node(graph,node['NODE_CHILD'])
    graph = cf.add_node(graph,node,user,user)

    json = cf.compose_graph(graph,user)    

    swift_conn.put_object(user,user,json)

    return acl_old


def delete_unnecessary_node(swift_conn,user,node,first_call_check):

    graph = get_graph(user)
    
    if first_call_check:
        f_node = get_node(graph,node['NODE_CHILD']) 
        if f_node == None:
            return None
    
    graph = remove_node(graph,node['NODE_CHILD'])
    json = compose_graph(graph,user)
    swift_conn.put_object(user,user,json)
        
    return node['ACL_CHILD']


def consumer_task():

    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='daemon10', durable=True)
           
    channel.basic_qos(prefetch_count=1)    
    channel.basic_consume(receive_message,
                      queue='daemon10')

    print(' [%d] Waiting for messages...' % os.getpid())
    channel.start_consuming()


def receive_message(ch, method, properties, body):
        
    #print(' [%d] Received' % os.getpid())
    command,sender_id,node = body.split('#')
    node = json.loads(node.decode('latin-1'), strict=False)
    #if command == 'CREATE':
    #    create_container(sender_id)    
    if command == 'INSERT':
        print "*****************************************"
        print node
        acl_list = cf.stringTOlist(node['ACL_CHILD'])
        token = node['CRYPTOTOKEN']
        swift_conn = swiftclient.client.Connection(user= ADMIN_USER, key= ADMIN_PASS, authurl= AUTH_URL,
                                                       tenant_name= sender_id, auth_version='2.0')
        old_acl_list = cf.stringTOlist(insert_new_node(swift_conn,sender_id,token,node,True))
        removed_users = set(old_acl_list).difference(set(acl_list))
        for user_id in set(acl_list).difference(set(sender_id)): 
            swift_conn = swiftclient.client.Connection(user= ADMIN_USER, key= ADMIN_PASS, authurl= AUTH_URL,
                                                       tenant_name= user_id, auth_version='2.0')
            insert_new_node(swift_conn,user_id,token,node,False)
        for user_id in removed_users:
            swift_conn = swiftclient.client.Connection(user= ADMIN_USER, key= ADMIN_PASS, authurl= AUTH_URL,
                                                       tenant_name= user_id, auth_version='2.0')
            delete_unnecessary_node(swift_conn,user_id,node,False)            
    elif command == 'REMOVE':
        acl_list = delete_unnecessary_node(swift_conn,sender_id,node,True)
        if acl_list != None:
            list_usr = stringTOlist(acl_list)
            list_usr.remove(sender_id)
            for user_id in list_usr:
                swift_conn = swiftclient.client.Connection(user= ADMIN_USER, key= ADMIN_PASS, authurl= AUTH_URL,
                                                       tenant_name= user_id, auth_version='2.0')
                delete_unnecessary_node(swift_conn,user_id,node,False)
            
    print(' [%d] Done!' % os.getpid())
    ch.basic_ack(delivery_tag = method.delivery_tag)


def create_consumer(n,clist):
    
    for i in range(1,n):
        
        pid = os.fork()
        if pid:
            clist.append(pid)
        else: consumer_task()
        print ('             **** CREATED [%d] ****' % (pid))
    
    return

def handler(signum,frame):
     for pid in ctrl_list:
         proc = psutil.Process(pid)
         proc.kill()
         ctrl_list.remove(pid)
     proc = psutil.Process(os.getpid())
     proc.kill()



def kill_consumer(clist):

    i = 0

    for pid in clist:
        if i >= ctrlen/4:
            break
        proc = psutil.Process(pid)
        if proc.status == psutil.STATUS_SLEEPING:
            proc.kill()
            i += 1
            clist.remove(pid)
            print ('             **** DELETED IDLE [%d] ****' % (pid))

    return


def check_status():

    count = 0

    for pid in ctrl_list:
        proc = psutil.Process(pid)
        #print(' PID [%d] status [%s]' % (pid, proc.status))
        if proc.status == psutil.STATUS_SLEEPING:
            count += 1
        elif proc.status == psutil.STATUS_RUNNING:
            count -= 1
        else: sys.stderr.write('Error on Process Status')

    return count


if __name__ == '__main__':

    # Require an admin connection
    kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_PASS, tenant_name=ADMIN_TENANT, auth_url=AUTH_URL)
    this_user = filter(lambda x: x.username == ADMIN_USER, kc_conn.users.list())
    UUID = this_user[0].id   

    admin_role = kc_conn.roles.find(name='admin')
    
    N_INI = 1 
    ctrl_list = []

    signal.signal(signal.SIGINT,handler)

    
    create_consumer(N_INI+1,ctrl_list)
    
    while(True):

        count_sleep = check_status()

        ctrlen = len(ctrl_list)
        threshold = 3/4*ctrlen

        if count_sleep > threshold and count_sleep > N_INI:
            kill_consumer(ctrl_list)
        elif -count_sleep > ctrlen*3/4:
            create_consumer(ctrlen/2,ctrl_list)
        elif -count_sleep > ctrlen/2:
            create_consumer(ctrlen/3,ctrl_list)

        time.sleep(3)      
    
    # never reached
