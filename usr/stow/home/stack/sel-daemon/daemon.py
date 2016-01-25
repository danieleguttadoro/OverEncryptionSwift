#!/usr/bin/env python

print "Started!!!!"

import os, sys, psutil, time, pika
from multiprocessing import Process
#from keystoneclient.v3 import client
#from keystoneclient import session
#from keystoneclient.auth import base
#from swift.proxy import server
import  swiftclient


def consumer_task():

    while (True):

        connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='daemon', durable=True)
           
        channel.basic_qos(prefetch_count=1)    
        channel.basic_consume(callback,
                      queue='daemon')

        #print swift_conn.head_account()
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    # never reached
    return


def callback(ch, method, properties, body):
        
    print(" [x] Received %r" % body)
    
    #time.sleep(body.count(b'.'))
    #req = Request.blank()
     

    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)


def create_consumer(n,clist):
    
    for i in range(1,n):
        pid = os.fork()
        if pid:
            clist.append(pid)
        else: consumer_task()
        print ('             **** CREATED [%d] ****' % (pid))
    
    return


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
        print(' PID [%d] status [%s]' % (pid, proc.status))
        if proc.status == psutil.STATUS_SLEEPING:
            count += 1
        elif proc.status == psutil.STATUS_RUNNING:
            count -= 1
        else: sys.stderr.write('Error on Process Status')

    return count


if __name__ == '__main__':

    swift_conn = swiftclient.client.Connection(
            user= 'admin', key= 'secretsecret', authurl= 'http://localhost:5000/v3',
            tenant_name= 'admin', auth_version='3')

    print swift_conn.head_account()

    """ auth = client.Client(username = 'admin',
                         password = 'secretsecret',
                         project_name = 'admin',
                         auth_url = 'http://localhost:5000/v3')

    x_auth_token = auth.get_headers(None)

    sess = session.Session(auth=auth)
    
    auth_plugin = base.BaseAuthPlugin()
    
    x_auth_token = auth_plugin.get_headers(sess)

    print ('AUTH: [%s]' % x_auth_token)
    """
    N_INI = 8
    ctrl_list = []

    create_consumer(N_INI+1,ctrl_list)

    while(True):

        count_sleep = check_status()

        ctrlen = len(ctrl_list)
        threshold = 3/4*ctrlen

        if count_sleep > threshold and count_sleep > N_INI:
            kill_consumer(ctrl_list)
        elif -count_sleep > ctrlen*3/4:
            print "qui qui qui qui"
            create_consumer(ctrlen/2,ctrl_list)
        elif -count_sleep > ctrlen/2:
            print "qua qua qua qua qua"
            create_consumer(ctrlen/3,ctrl_list)

        time.sleep(3)
    
    # never reached
  
