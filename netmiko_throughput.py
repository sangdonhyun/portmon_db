#-*- coding:utf-8 -*-
import os
import errno
import datetime
from netmiko import ConnectHandler
import ConfigParser
import common
import re
import glob
import redis
import time
import threading
import portinfo_insert
import sys
import fleta_dbms
from pysnmp.hlapi import *
import errdump

class netmiko():
    def __init__(self,swname,portInfo):
#         print portInfo
        self.sw_serial=swname
        print "Brocade serial :",self.sw_serial
#         portInfo.pop('name')
        
        self.portInfo=portInfo
        self.cfg=self.getCfg()
        self.cmdList=self.getCmdList()
#         print portInfo.values()
        self.ip = portInfo['ip']
        self.online_port_list=[]
        
        self.name = swname
        self.rdb=fleta_dbms.FletaDb()
#         self.portInfo.pop('name')
        
        self.password=portInfo['password']
        self.username=portInfo['username']
        self.fileName=os.path.join('data','%s_%s.tmp'%(self.name,self.ip,))
        self.com=common.Common()
       
        self.net_connect = ConnectHandler(**self.portInfo)
        self.portinfolist=[]
        self.portlist=[]
        self.r=self.redis()
        self.now=datetime.datetime.now()
        self.store_time=self.now.strftime('%Y-%m-%d %H:%M:%S')
        self.lhour=''
#         
#         self.r.config_set('requirepass', 'kes2719!')
    
    
    def get_line_set(self):
        with open(self.fileName) as f:
            lineset=f.readlines()
        return lineset
    def redis(self):
        redis_ip=self.cfg.get('redis','host')
        redis_port=self.cfg.get('redis','port')
        redis_passwd=self.cfg.get('redis','password')
        return redis.StrictRedis(host=redis_ip,port=int(redis_port),db=0,password=redis_passwd)
    
    def run(self):

#         net_connect = ConnectHandler(**self.portInfo)
        for cmd in self.cmdList:
            title='###***%s***###'%cmd
            self.fileWrite(title)
            output = self.net_connect.send_command(cmd)
#             print output
            self.fileWrite(output)
        
   

        
    def getCfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
#         print cfgFile,os.path.isfile(cfgFile)
        cfg.read(cfgFile)
        return cfg
    
    def fileWrite(self,msg,wbit='a'):
        with open(self.fileName,wbit) as f:
            f.write(msg+'\n')    
    def getCmdList(self):
        cmdList=[]
        for cmdno in sorted(set(self.cfg.options('command'))):
            cmd=self.cfg.get('command',cmdno)
            cmdList.append(cmd)
        
        return cmdList
    def set_check_date(self,check_date,status,serial):
        qeury_string="UPDATE ref.ref_code_san_info SET check_date='{}', collect_stat='{}'  WHERE swi_serial='{}'".format(check_date,status,serial)
        self.rdb.queryExec(qeury_string)
        



    def main(self):
        headmsg=self.com.get_module_head_msg(s_hostname=self.name,s_ip=self.ip)
        print headmsg
        self.fileWrite(headmsg, 'w')
        self.run()
        self.expectCmd()
        endmsg = self.com.get_module_tail_msg()
        self.fileWrite(endmsg)
        
        store_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.fread(self.fileName)
        self.line_tot_set=self.get_line_set()
        # errdump -> snmp
        errdump.err_dump(self.fileName).main()

        self.net_connect.disconnect()
        self.set_check_date(store_time,True,self.sw_serial)

    def expectCmd(self):
        ret=self.net_connect.send_command_expect(
         "portperrfshow",
         expect_string="Total",
         delay_factor=5,
        )
        self.fileWrite('###***portperfshow***###')
#         print ret
        if type(ret) == 'unicode':
            self.fileWrite(ret.decode('utf-8'))
        else:
            self.fileWrite(ret)
    def getPortNum(self,port):
        no = 0
        num = 0
        
        
        for portinfo in self.portinfolist:
           
            if int(portinfo['portindex']) == int(port):
                num = no
                break
            no = no +1
        return num
    
    
                
                
    
    def fread(self,file):
        
        portinfolist=[]
        portlist=[]
        crcBit,txBit,rxBit=False,False,False
        with open(file) as f:
            rd=f.read()

        
        lineset=rd.splitlines()
        self.line_tot_set=lineset
        num = 0
        slot,pnum,portnum=0,0,0
        slotnum=1
        serial=''
        portnum = 0
        portmax = 0
        serialBit = False
        txlist=[]
        rxlist=[]
        
        event_time=''
        onlineBit=False
        for i in range(len(lineset)) :
            line=lineset[i]
#             print line
            portinfo={}
            
            if  '#   EXECUTE DATE :' in line:
                event_time = ''.join(line.split('EXECUTE DATE :')[1:])
                event_time = event_time.replace('#','').strip()
                 
                 
            if  '#### DATA TIME :' in line:
                event_time = ''.join(line.split('EXECUTE DATE :')[1:])
                event_time = event_time.replace('#','').strip()
#                 
            if '###***switchshow***###' in line:
                onlineBit= True
            title_line_set=[]
            if onlineBit:
                linenum=1
                
                if 'Port' in line and 'Status' in line:
                    title_line_set=line.split()
                    title_line_set['Port']
                    port_line_num=title_line_set.index('Port')
                    status_line_num=title_line_set.index('Status')
#                     print len(title_line_set)
                    
                if 'Online' in line:
#                     print line
                    linetmp=line.split()
                    port_num =linetmp[linenum]
                    if len(linetmp) >= len(title_line_set):
                        self.online_port_list.append(port_num)
                        
            
            if '###***chassisshow***###' in line:
                serialBit= True
                onlineBit = False
            if serialBit:
                
                if 'Factory Serial Num:' in line:
                    
                    serial = line.split(':')[1].strip()
                    serialBit = False
                    
            
            
            
            if '###***' in line:
                crcBit,txBit,rxBit,thBit=False,False,False,False
            if '###***porterrshow***###' in line:
                crcBit=True
            
            if crcBit:
                crcset= line.split()
#                 print len(crcset),crcset
#                 print line
#                 print len(crcset) > 10 and 'frames' not in line and 'tx' not in line 
#                 print '-'*40
                if len(crcset) > 10 and 'frames' not in line and 'tx' not in line :
                    portinfo={}
                    portnum=crcset[0]
                    portnum=portnum.replace(':','')
                    
                    portinfo['portindex'] =   portnum
                    
                    portinfo['crcerr'] = crcset[4]
#                     if datetime =='':
#                         datetime = time.strftime('%Y-%m-%d %H:%M:%S')
#                     portinfo['datetime'] = datetime 
                    portinfo['serial'] = self.sw_serial
                    
                    self.portinfolist.append(portinfo)
                    self.portlist.append(portnum)
                    
                    
                    
#                     print '-'*50
#                     print crcset[0]
#                     print crcset
#                     print line
#                     print portnum
#                     print portinfo
#             
                        
            if '###***sfpshow -all***###' in line:
                
                rxBit = True
                
                
            if rxBit:
                
                
                if re.search('^Slot ', line) :
                    
                    slotline=line
                    slotline=slotline.replace('Slot','')
                    slotline=slotline.replace('/Port','')
                    slotline=slotline.replace(':','')
                    stset= slotline.split()
                    slot=int(stset[0])
                    pnum=int(stset[1])
                    
                    
                    listnum=self.getPortNum(self.portlist[num])
                    portinfo = self.portinfolist[listnum]
                    portinfo['slot'] = slot
                    portinfo['portnum'] = pnum
                    
                    
                    self.portinfolist[listnum] = portinfo
                    num = num +1
                
                 
                if re.search('^Port', line)  and 'SFP' not in line:
                    pnum = line.split()[1].strip()
                    pnum = pnum.replace(':','')
                    slot=0
                    #print line,pnum,slot,len(self.portinfolist)
                    
                    portinfo=self.portinfolist[int(num)]
                    
                    portinfo['slot'] = slot
                    portinfo['portnum'] = portinfo['portindex']
                    #print self.portinfolist[-1]
                    self.portinfolist[int(num)] = portinfo 
                    num = num +1
                    
                if ' GE: Port' in line:
                    
                    
                    try:
                        listnum=self.getPortNum(self.portlist[num])
                        portinfonum=self.portinfolist.index(listnum)
                        del self.portinfolist[portinfonum]
                    except:
                        pass
                    
                    num = num +1 
                    
                if 'TX Power: ' in line:
                    if 'uWatts' in line:
                        tx=line.split('(')[1].split(')')[0]
                        tx=tx.replace('uWatts','')
                        tx=tx.replace('uW','')
                    else:
                        
                        if '(' in line:
                            tx=line.split('(')[1].split(')')[0]
                            tx=tx.replace('uWatts','')
                            tx=tx.replace('uW','')
                        else:
                            tx=line.split()[2]
                        if 'inf' in tx:
                            tx='0'
                        
                    listnum=self.getPortNum(self.portlist[num-1])
                    
                    portinfo = self.portinfolist[listnum]
                    portinfo['tx'] = tx
                   
                    self.portinfolist[listnum] = portinfo
#                     crcerr = portinfolist[listnum]['crcerr']
#                     portinfolist[listnum] = {'num' : portlist[num],'tx' : tx,'crcerr' : crcerr }
                    
                    
                if 'RX Power:' in line:
                    
#                     print line
                    'uWatts'
                    if 'uWatts'  in line:
                        rx=line.split('(')[1].split(')')[0]
                        rx=rx.replace('uWatts','')
                        rx=rx.replace('uW','')
                        
                    else:
                        #print line
                        
                        if '(' in line:
                            rx=line.split('(')[1].split(')')[0]
                            rx=rx.replace('uWatts','')
                            rx=rx.replace('uW','')
                        else:
                            rx=line.split()[2]
                        if 'inf' in rx:
                            rx='0'
#                     print 'RX :',rx
                    
                    #sys.exit()
                    listnum=self.getPortNum( self.portlist[num-1])
                    
                    
                    portinfo = self.portinfolist[listnum]
                    
                    portinfo['rx'] = rx
                    self.portinfolist[listnum] = portinfo
                
            if '###***portperfshow***###' in line:
                thBit=True
                thList=[]
#                 print thBit
                if '###############################################################################' in line:
                    thBit=False
                
                if thBit:
                    linenum=i+1
                    a=0
                    for cnt in range(i+1,len(lineset)):
                        
                        num=a % 4
#                         print lineset[cnt],num,cnt,i,linenum,a,len(lineset[cnt].split())
                        if num==2 and len(lineset[cnt].split()) > 0:
                        
#                             print lineset[cnt]
                            thList=thList+lineset[cnt].split()
                        a=a+1
            
                        
        resutllist=[]
        for i in range(len(self.portinfolist)):
            portInfo=self.portinfolist[i]
            th = thList[i]
            if th[-1] == 'k':
#                 print th
                th = th.replace('k','')
                th = float(th) * 1024
#                 print th
                
            elif th[-1] == 'm':
#                 print th
                th = th.replace('m','')
                th = float(th) * 1024 *1024
#                 print th
            else:
                try:
                    th = float(th)
                except:
                    th = 0
                    pass
                   
            if 'tx' not in portInfo.keys():
                portInfo['tx']='0'
                portInfo['rx']='0'
                
            portInfo['throughput']=th
            
            if 'slot' in portinfo.keys():
                resutllist.append(portinfo)
                
#         se=serial.zfill(20)
        key='%s::SAN_SWICH_PERFROM::%s'%(self.store_time,self.sw_serial)
        lastkey='LASTKEY::%s'%self.sw_serial
        self.r.set(lastkey,key)
        print 'portinfo list:',len(self.portinfolist)
        print self.portinfolist
        print '-'*50
        print self.online_port_list
        print '-'*50
        port_info_list=[]
        for port_info in self.portinfolist:
            if port_info['portindex'] in self.online_port_list:
                port_info_list.append(port_info)
        self.portinfolist=port_info_list
        print 'portinfo list:',len(self.portinfolist)
        print self.portinfolist
        
        self.r.lpush(key,str(self.portinfolist))
        portinfo_insert.inst(self.portinfolist,self.store_time,event_time)

        self.setRedis()
        return True
   
    def setRedis(self):
        print self.portinfolist[0]
        serial=self.portinfolist[0]['serial']
        lasthour=self.now.strftime('%Y-%m-%d %H')
        lkey='brocade_latest_time_{}'.format(self.sw_serial)

        print lkey
        self.r.set(lkey,self.store_time)
        self.r.expire(lkey,datetime.timedelta(days=2))
        lkey='brocade_latest_time_{}_{}'.format(self.sw_serial,lasthour)        
        print lkey
        self.r.rpush(lkey,self.store_time)
        self.r.expire(lkey,datetime.timedelta(days=2))
        for portInfo in self.portinfolist:
            
            portindex=portInfo['portindex']
#             device = portInfo['serial']
            device = self.sw_serial
            sfp_tx=portInfo['tx']
            sfp_rx=portInfo['rx']
            crc=portInfo['crcerr']
            throughput=portInfo['throughput']
            pkey='{}::{}::SFP_TX_POWOR'.format(self.store_time,device)
            self.r.hset(pkey,portindex,sfp_tx)
            self.r.expire(pkey,datetime.timedelta(days=2))
            print pkey
            pkey='{}::{}::SFP_RX_POWOR'.format(self.store_time,device)
            print pkey,sfp_rx
            self.r.hset(pkey,portindex,sfp_rx)
            self.r.expire(pkey,datetime.timedelta(days=2))
            print pkey
            pkey='{}::{}::CRC'.format(self.store_time,device)
            self.r.hset(pkey,portindex,crc)
            self.r.expire(pkey,datetime.timedelta(days=2))
            pkey='{}::{}::throughput'.format(self.store_time,device)
            print pkey
            self.r.hset(pkey,portindex,throughput)
            self.r.expire(pkey,datetime.timedelta(days=2))

            
class manager():
    def __init__(self):
        self.swlist=self.getList()
        self.rdb=fleta_dbms.FletaDb()
        self.cfg=self.getCfg()
    
    def getCfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
#         print cfgFile,os.path.isfile(cfgFile)
        cfg.read(cfgFile)
        return cfg
    
    def
        (self):
        """
[000000000ALJ2503G08G]
device_type = brocade_nos
ip = 10.10.10.20
username = admin
password = password
port = 22
secret = False
verbose = False
        """
        cj_center=self.cfg.get('swi_center','cj')
        if ',' in cj_center:
            cj_list=[]
            for cj in cj_center.split(','):
                cj_list.append(cj)
            str="','".join(cj_list)
        print str
        query_string="SELECT swi_serial, device_type, create_ip, user_name, pass_word, port, secret, verboses  FROM ref.ref_code_san_info where swi_center in ('"+str+"')"
        

#         print query_string
        rows=self.rdb.getRaw(query_string)
        swList=[]
        for row in rows:
#             print row
            sw={}
            sw['name']=row[0]
            sw['ip']=row[2]
            sw['username']=row[3]
            sw['password']=row[4]
            sw['device_type']=row[1]
            sw['secret']=False
            sw['verbose']=False
            
#             print sw
            
            if sw['ip'] <> None:
                pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
                isip = pat.match(sw['ip'])
                if isip:
                    swList.append(sw)
        
        return swList
                 
    def getList(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        
        swList=[]
        for sec in sorted(set(cfg.sections())):
            hostInfo={}
            hostInfo['name'] = sec
            for opt in cfg.options(sec):
#                 print cfg.get(sec,opt)
                hostInfo[opt] = cfg.get(sec,opt)
#             print hostInfo
            swList.append(hostInfo)
        
        
        return swList
    
    def main(self):
#         swList=self.getListDb()
        swList=self.getList()  # list.cfg 
        print 'sw cnt :',len(swList)
        for sw in swList:
#             print sw
#             print sw.keys()
            if 'name' in sw.keys():
                swname=sw['name']
                sw.pop('name')
#                 print swname,sw
                try:
                    netmiko(swname,sw).main()
                except:
                    pass
                
    def run(self):
        self.main()
            
        
 
print("Main Thread")

if __name__=='__main__':
#     portInfo={'username': 'admin',  'ip': '121.170.193.209', 'secret': 'False', 'device_type': 'brocade_nos', 'password': 'password', 'port': '20001', 'verbose': 'False'}
#     print portInfo
#     swname='fsw02'
    
    manager().run()
    
    
#     while True:
#         try:
#             netmiko(swname,portInfo).main()
#         except:
#             pass
#         print '#'*60
#         print 'time sleep 60 sec'
#         time.sleep(60)
