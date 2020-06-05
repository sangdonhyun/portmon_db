#-*- coding:utf-8 -*-
'''
Created on 2019. 11. 19.

@author: user
'''
import threading, time
import netmiko_throughput as perf

      

def portmon(swname,sw):
    print 'swname :',swname
    perf.netmiko(swname,sw)
#     th.netmiko(swname,sw).main()
 
def getSwList(swList):
    for sw in swList:
        print sw
        if 'name' in sw.keys():
            swname=sw['name']
            sw.pop('name')
#             th.netmiko(swname,sw).main()
        t1 = threading.Thread(target=portmon, args=(swname,sw,))
    t1.daemon = True
    t1.start() 
     
if __name__=='__main__':
    swList=perf.manager().getList()
    print len(swList)
    getSwList(swList)

