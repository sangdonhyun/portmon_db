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
import errdump_str
def set_check_date(check_date,status,serial):
    qeury_string="UPDATE ref.ref_code_monitor_san_info  SET  perm_check_date='{}'  , perm_collect_stat='{}'  WHERE swi_serial='{}'".format(check_date,status,serial)
    
    rdb=fleta_dbms.FletaDb()
    rdb.queryExec(qeury_string)


class netmiko():
    def __init__(self,swname,portInfo,store_time):
#         print portInfo
        self.sw_serial=swname
        self.store_time=store_time
        print "Brocade serial :",self.sw_serial
        self.event_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        if 'targetList' in self.portInfo.keys():
            self.targetList=self.portInfo['targetList']
            self.portInfo.pop('targetList')
        else:
            self.targetList={'log_bit':False,'crc_bit':False,'sfp_bit':False,'througput_bit':False}
        self.password=portInfo['password']
        self.username=portInfo['username']
        self.fileName=os.path.join('data','%s_%s.tmp'%(self.name,self.ip,))
        self.com=common.Common()
       
        self.net_connect = ConnectHandler(**self.portInfo)
        self.portinfolist=[]
        self.portlist=[]
        self.r=self.redis()
        self.now=datetime.datetime.now()
        
        self.lhour=''
        self.portValue={}
        self.slot_bit = False
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
        
   
    def exec_cmd(self,cmd):
        try:
            output = self.net_connect.send_command(cmd)
        except:
            output=''
        return output
    
        
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
        

    def getSerial(self):
        cmd='chassisshow'
        title='###***{}***###'.format(cmd)
        self.fileWrite(title)
        ret=self.exec_cmd(cmd)
#         print ret
        self.fileWrite(ret)
        serial=None
        for line in ret.splitlines():
            if 'Factory Serial Num:' in line:
                serial = line.split(':')[1].strip()
        
        real_serial=self.getRealSerial(serial)
        return real_serial

    def getRealSerial(self,serial):
        query_string=""""SELECT swi_serial
  FROM live.live_swi_brocade_serial_info where chk_swi_serial = '{}';
""".format(serial)
        rows=self.rdb.getRaw(query_string)
        real_serial=None
        try:
            real_serial=rows[0][0]
        except:
            real_serial=None
            
        return real_serial



    def is_online(self,portindex):
        online_port=self.portValue.keys()
        if portindex in online_port:
            return True
        else:
            return False

    def is_online_port(self,slot,portnum):
        # print self.portValue
        online_port_index = None
        online_bit = False
        onlines= self.portValue.keys()
        slot = str(slot)
        portnum = str(portnum)
        for port_index in onlines:
            # print port_index,self.port_info[port_index]
            # print slot,portnum,self.port_info[port_index]['slot'] ,self.port_info[port_index]['portnum']


            if self.portValue[port_index]['slot'] == slot.strip() :
                if  self.portValue[port_index]['portnum'].strip() == portnum.strip():
                    online_bit = True
                    break
        return port_index,online_bit

    def getPortIndex(self,slot,portnum):
        for key in self.portValue.keys():
            slot= self.portValue[key][slot]
            sportnum = self.portValue[key][slot]
            if slot==slot and portnum == sportnum:
                port_index=key
        return port_index

    def get_portindex(self,s_slot,s_portnum):
        online_port = self.portValue.keys()
        re_port_index = None
        for port_index in online_port:
            slot = self.portValue[port_index]['slot']
            portnum =self.portValue[port_index]['portnum']
            if slot == s_slot and s_portnum == portnum:
                re_port_index = port_index
        return re_port_index


    def getSfp(self):
        cmd='sfpshow -all'
        title='###***{}***###'.format(cmd)
        self.fileWrite(title)
        ret=self.exec_cmd(cmd)
#         print ret
        portindex = None
        online_bit = False
        line_set = ret.splitlines()
        for i in range(len(line_set)):
            line = line_set[i]

            if self.slot_bit:
                if re.match('^Slot', line):
                    line_sp = line.split('/')
                    slot = line_sp[0]
                    slot = slot.replace('Slot', '')
                    port = line_sp[1]
                    port = port.replace(':', '')
                    port = port.replace("Port", '')
                    portindex = self.get_portindex(int(slot), int(port))
                if not portindex == None:
                    if self.is_online(int(portindex)):
                        if re.match('^RX', line):
                            rx = line.split('(')[1]
                            rx = rx.replace(')', '')
                            rx = rx.replace('uW', '')
                            self.portValue[int(portindex)]['rx'] = rx
                        if re.match('^TX', line):
                            tx = line.split('(')[1]
                            tx = tx.replace(')', '')
                            tx = tx.replace('uW', '')
                            self.portValue[int(portindex)]['tx'] = tx
            else:
                if re.match('^Port', line):
                    portindex = line.split()[-1]
                    portindex = portindex.replace(':', '')
                    online_bit = self.is_online(int(portindex))
                if online_bit:
                    if re.match('^RX', line):
                        rx = line.split(')')[0]
                        rx = rx.split('(')[1]
                        rx = rx.replace('uW', '')
                        self.port_info[int(portindex)]['rx'] = rx

                    if re.match('^TX', line):
                        tx = line.split(')')[0]
                        tx = tx.split('(')[1]
                        tx = tx.replace('uW', '')
                        print tx
                        self.port_info[int(portindex)]['tx'] = tx
                    
                
    
    def getValue(self,val):
        if 'k' in val:
            val=val.replace('k','')
            val=float(val)*1024
        elif 'm' in val:
            val=val.replace('m','')
            val=float(val)*1024*1024
        elif 'g' in val:
            val=val.replace('g','')
            val=float(val)*1024*1024*1024
        else:
            return val
        return val

    
    def getThroughput(self):
        ret=self.net_connect.send_command_expect(
         "portperfshow",
         expect_string="Total",
         delay_factor=5,
        )
        self.fileWrite('###***portperfshow***###')
        print '-'*50
#         print ret
        if type(ret) == 'unicode':
            self.fileWrite(ret.decode('utf-8'))
        else:
            self.fileWrite(ret)
        line_set=ret.splitlines()


#         print 'line set:'
#         print lineset
        

        port_list,value_list = [],[]
        if self.slot_bit:
            port_th_list=[]
            for i in range(len(line_set)):
                line=line_set[i]
                num= i%4
                if num == 0:
                    port_list=line.split()
                if num == 2:
                    line_sp = line.split()
                    slot = line_sp[1]
                    value_list =line_sp[2:]

                    for i in range(len(port_list)):
                        port = port_list[i]
                        val = value_list[i]
                        if not port == 'Total':
                            print 'slot,port ',slot,port
                            portindex = self.get_portindex(int(slot),int(port))
                            port_th_list.append([portindex,val])
            for th in port_th_list:
                try:
                    self.portValue[int(th[0])]['throughput'] = th[-1]
                except:
                    pass


        else:
            for i in range(len(line_set)):
                line=line_set[i]
                num= i%4
                if num == 0:
                    port_list=port_list+line.split()
                if num == 2:
                    value_list =value_list + line.split()

            # print port_list
            # print value_list
            for i in range(len(port_list)):
                portnum = port_list[i]
                value = value_list[i]
                if not portnum == 'Total':
                    if self.is_online(int(portnum)):
                        # print portnum, value
                        self.portValue[int(portnum)]['throughput'] = value
            
        

    def getOnlinePort(self):
        cmd='switchshow'
        online_port_list=[]
        self.fileWrite('###***{}***###'.format(cmd))
        ret=self.exec_cmd(cmd)
        # print ret
        slot_bit=False
        if re.search('Slot',ret):
            slot_bit=True
        # print slot_bit
        self.fileWrite(ret)
        if 'Slot' in ret:
            self.slot_bit = True

        line_set = ret.splitlines()
        for i in range(len(line_set)):
            line = line_set[i]

            if 'Online' in line:
                line_sp = line.split()

                if 'FC' in line:
                    if self.slot_bit:
                        portindex = int(line_sp[0])
                        slot = int(line_sp[1])
                        portnum = int(line_sp[2])
                        print {'portindex': portindex, 'slot': slot, 'portnum': portnum}
                        self.portValue[portindex] = {'portindex': portindex, 'slot': slot, 'portnum': portnum}
                    else:
                        portindex = int(line_sp[0])
                        slot = 0
                        portnum = int(line_sp[1])
                        self.portValue[portindex] = {'portindex': portindex, 'slot': slot, 'portnum': portnum}
                        
        return online_port_list
    def result_update(self,resutl):
        query="update ref.ref_code_monitor_san_info set perm_check_date='{}',perm_collect_stat='{}' where swi_serial='{}'".format(self.store_time,'True',self.sw_serial)
    def getCrc(self):
        cmd='porterrshow'
        self.fileWrite('###***{}***###'.format(cmd))
        ret=self.exec_cmd(cmd)
        self.fileWrite(ret)
        for line in ret.splitlines():
#             print line
            lineTmp= line.split()
            portindex=lineTmp[0]
            if ':' in portindex:
                portindex=portindex.replace(':','')
            if portindex in self.online_port_list:
                crc= str(lineTmp[4])
                self.portValue[portindex]['crcerr']=crc
#                 print 'CRC :',crc
#                 print self.portValue
    def main(self):
        headmsg=self.com.get_module_head_msg(s_hostname=self.name,s_ip=self.ip)
        
        print headmsg
        self.getOnlinePort()
        print 'online-port-list :'
        print self.portValue.keys()
        self.fileWrite(headmsg, 'w')
        cmd='date'
        title='###***{}***###'.format(cmd)
        self.fileWrite(title)
        ret=self.exec_cmd(cmd)
        self.fileWrite(ret)
        
#         self.onlinePort=self.getOnlinePort()
        
        print 'SFP bit :',self.targetList['sfp_bit']
        
        if self.targetList['sfp_bit']:
            self.getSfp()
        else:
            for key in self.portValue.keys():
                self.portValue[key]['tx'] = '-1'
                self.portValue[key]['rx'] = '-1'
            
        print 'Port value:',self.portValue
        print 'crc_bit',self.targetList['crc_bit']
        if self.targetList['crc_bit']:
            self.getCrc()
        else:
            for key in self.portValue.keys():
                self.portValue[key]['crcerr'] = '-1'
        if self.targetList['throughput_bit']:
            self.getThroughput()
        else:
            for key in self.portValue.keys():
                self.portValue[key]['throughput'] = '-1'
            
        print '-'*50
        
        print 'Port value:',self.portValue
        portvaluelise=self.sort_portValue()
#         print portvaluelise
        self.setRedisLastkey(portvaluelise)
        self.setRedis(portvaluelise)
#         print portvaluelise
        portinfo_insert.inst(portvaluelise,self.store_time,self.event_time)
        self.result_update('True')
#         print self.fileName
#
#         
#         self.targetList['log_bit']
#         
#         if self.targetList['throughput_bit']:
#             self.getThroughput()
#         
# #         self.run()
#         self.expectCmd()
#         endmsg = self.com.get_module_tail_msg()
#         self.fileWrite(endmsg)
#         
#         store_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         
#         self.fread(self.fileName)
#         self.line_tot_set=self.get_line_set()
#         
        if self.targetList['log_bit']:
            # errdump -> snmp
            cmd='errdump'
            self.fileWrite('###***{}***###'.format(cmd))
            ret=self.exec_cmd(cmd)
            self.fileWrite(ret)
            errdump_str.err_dump(self.sw_serial,ret).main()
            
        self.net_connect.disconnect()
        set_check_date(self.store_time,True,self.sw_serial)

    def expectCmd(self):
        ret=self.net_connect.send_command_expect(
         "portperfshow",
         expect_string="Total",
         delay_factor=5,
        )
        self.fileWrite('###***portperfshow***###')
#         print ret
        if type(ret) == 'unicode':
            self.fileWrite(ret.decode('utf-8'))
        else:
            self.fileWrite(ret)
        return ret
    def getPortNum(self,port):
        no = 0
        num = 0
        
        
        for portinfo in self.portinfolist:
           
            if int(portinfo['portindex']) == int(port):
                num = no
                break
            no = no +1
        return num
    
    
                
                
    
    
    def sort_portValue(self):
        portvaluelist=[]
        for portindex in sorted(self.portValue.keys()):
            print 'port index :',portindex
            portinfo=self.portValue[portindex]
            portinfo['portindex'] = portindex
            portinfo['serial'] = self.sw_serial
            print portinfo
            portvaluelist.append(portinfo)

        
        return portvaluelist
    
    def setRedisLastkey(self,portvaluelist):
#         se=serial.zfill(20)
        key='%s::SAN_SWICH_PERFROM::%s'%(self.store_time,self.sw_serial)
        lastkey='LASTKEY::%s'%self.sw_serial
        self.r.set(lastkey,key)
        
        """
        "[{'slot': 0, 'portindex': '0', 'portnum': '0', 'tx': '465.5 ', 'rx': '541.8 ', 'throughput': 4198.4, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}, {'slot': 0, 'portindex': '1', 'portnum': '1', 'tx': '468.9 ', 'rx': '350.7 ', 'throughput': 25292.8, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}, {'slot': 0, 'portindex': '4', 'portnum': '4', 'tx': '455.9 ', 'rx': '420.3 ', 'throughput': 200.0, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}, {'slot': 0, 'portindex': '5', 'portnum': '5', 'tx': '465.7 ', 'rx': '495.8 ', 'throughput': 96972.8, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}, {'slot': 0, 'portindex': '6', 'portnum': '6', 'tx': '454.4 ', 'rx': '212.9 ', 'throughput': 0.0, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}, {'slot': 0, 'portindex': '7', 'portnum': '7', 'tx': '470.4 ', 'rx': '201.3 ', 'throughput': 0.0, 'crcerr': '0', 'serial': '000000000AFY1929L00G'}]"
        """
        self.r.lpush(key,str(portvaluelist))
        
        
        
   
    def setRedis(self,portvaluelist):
        print portvaluelist[0]
        
        lasthour=self.now.strftime('%Y-%m-%d %H')
        lkey='brocade_latest_time_{}'.format(self.sw_serial)

        print lkey
        self.r.set(lkey,self.store_time)
        self.r.expire(lkey,datetime.timedelta(days=2))
        lkey='brocade_latest_time_{}_{}'.format(self.sw_serial,lasthour)        
        print lkey
        self.r.rpush(lkey,self.store_time)
        self.r.expire(lkey,datetime.timedelta(days=2))
        for portInfo in portvaluelist:
            
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
        self.store_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def getCfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
#         print cfgFile,os.path.isfile(cfgFile)
        cfg.read(cfgFile)
        return cfg
    
    def getListDb(self):
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
        query_string="""
SELECT swi_serial, device_type, 
   create_ip, user_name, pass_word, port, secret, verboses,
   event_log, crc, sfp, throughput
FROM ref.ref_code_monitor_san_info;
    """
        

#         print query_string
        rows=self.rdb.getRaw(query_string)
        
        swList=[]
        for row in rows:
#             print row
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
        swList=self.getListDb()
#         swList=self.getList()  # list.cfg 
        print 'sw cnt :',len(swList)
        
        for sw in swList:
#             print sw
#             print sw.keys()
            if 'name' in sw.keys():
                swname=sw['name']
                sw.pop('name')
                print swname,sw
                print self.store_time
                try:
                    netmiko(swname,sw,self.store_time).main()
                except:
                    print 'error :'
                
                
                
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
