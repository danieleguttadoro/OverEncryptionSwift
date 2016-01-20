import os, sys, psutil
from multiprocessing import Process, Pipe

#def control_task(conn):
#value = random.randint(1, 10)
#conn.send(value)
#print('Value [%d] sent by PID [%d]' % (value, os.getpid()))
#conn.close()

def consumer_task(conn):
print('Value [%d] received by PID [%d]' % (conn.recv(),
os.getpid()))

if __name__ == '__main__':
    #producer_conn, consumer_conn = Pipe()
    #consumer = Process(target=consumer_task,args=(consumer_conn,))
    #control = Process(target=control_task,args=(consumer_conn,))
    #consumer.start()
    #control.start()
    #consumer.join()
    #control.join()
    ctrl_list = []
    
    for i in range(1,9):
        consumer = Process(target=consumer_task))
        ctrl_list.append(os.getpid())
        consumer.start()
    
    while(True):

        count_idle = 0

        for pid in ctrl_list:
             proc = psutil.Process(pid)
             if proc.status() == psutil.STATUS_IDLE:
                count_idle += 1
             elif proc.status() == psutil.STATUS_RUNNING:
                count_idle -= 1
             else sys.stderr.write('Error on Process Status')

        ctrlen = len(ctrl_list)
        threshold = 3/4*ctrlen

        if count_idle > threshold:
            for pid in ctrl_list[threshold:]
                proc = psutil.Process(pid)
                proc.kill()
            ctrl_list = ctrl_list[:threshold-1]
        elif 2*abs(count_idle) > ctrlen
            for i in range (1,ctrlen/2):        
                consumer = Process(target=consumer_task))
                ctrl_list.append(os.getpid())
                consumer.start()




    #never reached??
    #for i in consumers
    #    i.join()
