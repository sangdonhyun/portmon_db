'''
Created on 2019. 12. 2.

@author: Administrator
'''
from ConfigParser import ConfigParser
'''
Created on 2019. 12. 2.

@author: user
'''
from multiprocessing import Pool
from multiprocessing import Process
import time
import os
import re
import math
import ConfigParser
import netmiko_throughput_db
import datetime
import fleta_dbms

def sshCon(hostname,hostInfo,sdate):
    print hostname,hostInfo

    netmiko_throughput_db.netmiko(hostname,hostInfo,sdate).main()

def getListDb():
        
    cfg=ConfigParser.RawConfigParser()
    cfgFile=os.path.join('config','config.cfg')
#         print cfgFile,os.path.isfile(cfgFile)
    cfg.read(cfgFile)    
    cj_center=cfg.get('swi_center','cj')
    if ',' in cj_center:
        cj_list=[]
        for cj in cj_center.split(','):
            cj_list.append(cj)
        str="','".join(cj_list)
    print str
    query_string="""
    SELECT swi_serial, device_type, 
       create_ip, user_name, pass_word, port, secret, verboses,
       event_log, crc, sfp, throughput
    FROM ref.ref_code_monitor_san_info;
    """
    
    rdb=fleta_dbms.FletaDb()
    print 'query :',query_string
    rows=rdb.getRaw(query_string)
    swList=[]
    
    
    
    for row in rows:
        log_bit=False
        crc_bit = True
        sfp_bit=True
        throughput_bit=True
        
        
        log_str = row[8]
        crc_str = row[9]
        sfp_str = row[10]
        thr_str = row[11]
        bitDic={}
        if log_str == 'O' :
            log_bit=True
        else:
            log_bit=False
        if crc_str == 'O' :
            crc_bit=True
        else:
            crc_bit=False
        if sfp_str == 'O' :
            sfp_bit=True
        else:
            sfp_bit=False
        if thr_str == 'O' :
            throughput_bit=True
        else:
            throughput_bit=False
#         print row
        bitDic['log_bit'] = log_bit
        bitDic['crc_bit'] = crc_bit
        bitDic['sfp_bit'] = sfp_bit
        bitDic['throughput_bit'] = throughput_bit
        sw={}
        sw['name']=row[0]
        sw['ip']=row[2]
        sw['username']=row[3]
        sw['password']=row[4]
        sw['device_type']=row[1]
        sw['secret']=False
        sw['verbose']=False
        sw['targetList'] = bitDic
#         print sw
        
        if sw['ip'] <> None:
            pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            isip = pat.match(sw['ip'])
            if isip:
                swList.append(sw)
    
    return swList
def getList():
    cfg=ConfigParser.RawConfigParser()
    cfgFile=os.path.join('config','list.cfg')
    cfg.read(cfgFile)
    hostList=[]
    for sec in cfg.sections():
        hostInfo={}
        hostInfo['name']=sec
        for opt in cfg.options(sec):
            hostInfo[opt] = cfg.get(sec,opt)
        hostList.append(hostInfo)
    return hostList




if __name__ == '__main__':
    
    procs = []
    

    # while True:
    sdate=datetime.datetime.now()
#         hostList=getList()
    hostList=getListDb()
    print hostList
    for hostInfo in hostList:
        hostname=hostInfo.pop('name')
        proc = Process(target=sshCon, args=(hostname,hostInfo,sdate.strftime('%Y-%m-%d %H:%M:%S'),))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    edate=datetime.datetime.now()
    diffsec=edate-sdate
    print "START :",sdate
    print "END   :",edate
    print "diff  ",diffsec
    print 'wait 60-17'
    time.sleep(60-17)

    
        
        
    