import os, sys, psutil, time, pika
from multiprocessing import Process, Pipe

#def control_task(conn):
#value = random.randint(1, 10)
#conn.send(value)
#print('Value [%d] sent by PID [%d]' % (value, os.getpid()))
#conn.close()

def consumer_task():

    while (True):

        connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='daemon', durable=True)
            
        
        channel.basic_qos(prefetch_count=1)    
        channel.basic_consume(callback,
                      queue='daemon')

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

def callback(ch, method, properties, body):
    
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

def create_consumer(n,clist):
    
    for i in range(1,n):
        pid = os.fork()
        if pid:
            clist.append(pid)
        else: consumer_task()
    
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
    #producer_conn, consumer_conn = Pipe()
    #consumer = Process(target=consumer_task,args=(consumer_conn,))
    #control = Process(target=control_task,args=(consumer_conn,))
    #consumer.start()
    #control.start()
    #consumer.join()
    #control.join()

    N_INI = 8
    ctrl_list = []

    create_consumer(N_INI+1,ctrl_list)

    while(True):

        count_sleep = check_status()

        ctrlen = len(ctrl_list)
        threshold = 3/4*ctrlen

        if count_sleep > threshold and count_sleep > N_INI:
            kill_consumer(ctrl_list)
            print ('             **** DELETED IDLE [%d] ****' % (pid))
        elif -count_sleep > ctrlen*3/4:
            create_consumer(ctrlen/2,ctrl_list)
            print ('             **** CREATED HALF [%d] ****' % (pid))
        elif -count_sleep > ctrlen/2:
            create_consumer(ctrlen/3,ctrl_list)
            print ('             **** CREATED THIRD [%d] ****' % (pid))

        time.sleep(3)

    #never reached??
