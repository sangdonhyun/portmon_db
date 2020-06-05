'''
Created on 2018. 11. 21.

@author: user
'''
import ConfigParser
import os
from multiprocessing import Lock, Process, Queue, current_process
import time
import queue # imported for using queue.Empty exception
import paramikoExample
import netmikoExample
import errPortLoad
def do_job(tasks_to_accomplish, tasks_that_are_done,portInfo):
    cfg=ConfigParser.RawConfigParser()
    cfgFile=os.path.join('config','config.cfg')
    cfg.read(cfgFile)
    try:
        module=cfg.get('server','module')
    except:
        module='paramiko'
    
    while True:
#         try:
#             '''
#                 try to get task from the queue. get_nowait() function will 
#                 raise queue.Empty exception if the queue is empty. 
#                 queue(False) function would do the same task also.
#             '''
#         task = tasks_to_accomplish.get_nowait()
        if module=='paramiko':
            paramikoExample.Paramiko(portInfo).main()
        else:
            print 'start netmiko module'
            print portInfo
            print '02 :',portInfo.keys()
            netmikoExample.netmiko(portInfo).main()
#         except queue.Empty:
#             print '#'*50
#             print '#'*50
#             print 'ERROR'
#             print portInfo
#             print '#'*50
#             print '#'*50
#             break
#         else:
#             '''
#                 if no exception has been raised, add the task completion 
#                 message to task_that_are_done queue
#             '''
#             print(task)
#             tasks_that_are_done.put(task + ' is done by ' + current_process().name)
#             time.sleep(.5)
    return True


class PortInfo():
    def __init__(self):
        self.hostlist=self.getHostList()
    
    def getHostList(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        
        hostList=[]
        for sec in sorted(set(cfg.sections())):
            hostInfo={}
#             print type(cfg.options(sec))
            hostInfo['name'] = sec
            for opt in cfg.options(sec):
#                 print cfg.get(sec,opt)
                hostInfo[opt] = cfg.get(sec,opt)
            hostList.append(hostInfo)
        print hostList
        return hostList
    
    def main(self):
        now = time.strftime("%y%m%d-%H%M%S")
        print now
        start_time = time.time()
        
        self.multiProcess()
        errPortLoad.Load().main()
        print("--- %s seconds ---" %(time.time() - start_time))
 

        
    def multiProcess(self):
        number_of_task = 10
        number_of_processes = 4
        tasks_to_accomplish = Queue()
        tasks_that_are_done = Queue()
        processes = []
    
        for i in range(len(self.hostlist)):
            tasks_to_accomplish.put("Task no " + str(i))
            print i,self.hostlist[i]
            portInfo=self.hostlist[i]
            print '01 :',portInfo.keys()
        # creating processes
#         for w in range(number_of_processes):

            p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done,portInfo))
            processes.append(p)
            p.start()
    
        # completing process
        for p in processes:
            p.join()
    
        # print the output
        while not tasks_that_are_done.empty():
            print(tasks_that_are_done.get())
    
    
        
        return True
        

if __name__ == '__main__':
#     main()
    print 'START'
    try:
        PortInfo().main()
    except:
        pass	
    print 'END'
    
    