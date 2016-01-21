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
        channel.queue_declare(queue='hello', durable=True)
            
        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)
            time.sleep(body.count(b'.'))
            print(" [x] Done")
            ch.basic_ack(delivery_tag = method.delivery_tag)
        
        channel.basic_qos(prefetch_count=1)    
        channel.basic_consume(callback,
                      queue='hello')

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

if __name__ == '__main__':
    #producer_conn, consumer_conn = Pipe()
    #consumer = Process(target=consumer_task,args=(consumer_conn,))
    #control = Process(target=control_task,args=(consumer_conn,))
    #consumer.start()
    #control.start()
    #consumer.join()
    #control.join()

    n_ini = 8
    ctrl_list = []
    
    for i in range(1,n_ini+1):
        pid = os.fork()
        if pid:
            ctrl_list.append(pid)
        else: consumer_task()

    while(True):

        count_sleep = 0

        for pid in ctrl_list:
             proc = psutil.Process(pid)
             print(' PID [%d] status [%s]' % (pid, proc.status))
             if proc.status == psutil.STATUS_SLEEPING:
                count_sleep += 1
             elif proc.status == psutil.STATUS_RUNNING:
                count_sleep -= 1
             else: sys.stderr.write('Error on Process Status')

        ctrlen = len(ctrl_list)
        threshold = 3/4*ctrlen

        if (count_sleep > threshold and count_sleep > n_ini):
            i = 0
            for pid in ctrl_list:
                if i >= ctrlen/4:
                    break
                proc = psutil.Process(pid)
                if proc.status == psutil.STATUS_SLEEPING:
                    proc.kill()
                    i += 1
                    ctrl_list.remove(pid)
                    print ('             **** DELETED IDLE [%d] ****' % (pid))
        elif -count_sleep > ctrlen*3/4:
            for i in range (1,ctrlen/2):        
                pid = os.fork()
                if pid:
                    ctrl_list.append(pid)
                else: consumer_task()
                print ('             **** CREATED HALF [%d] ****' % (pid))
        elif -count_sleep > ctrlen/2:
            for i in range (1,ctrlen/3):        
                pid = os.fork()
                if pid:
                    ctrl_list.append(pid)
                else: consumer_task()
                print ('             **** CREATED THIRD [%d] ****' % (pid))

        time.sleep(3)

    #never reached??
