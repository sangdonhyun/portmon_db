'''
Created on 2020. 2. 18.

@author: Administrator
'''
import os
import datetime
import ConfigParser
from pysnmp.hlapi import *


class err_dump():
    def __init__(self,fileName):
        self.fileName=fileName
        self.lineset=self.line_set()
        self.config_name=self.get_config_name()
        
        
    """
    severity : INFO, WARNING, ERROR, and CRITICAL.

    Timestamp , Message ID, External sequence number, securityu audit flag, severity, switch name, Message
    ###***errdump***###
Fabric OS: v6.2.0c
2020/02/14-05:14:16, [SEC-1193], 122405, FID 128, INFO, Fsw_01, Security violation: Login failure attempt via TELNET/SSH/RSH. IP Addr: 195.211.213.36
2020/02/14-05:14:22, [SEC-1193], 122406, FID 128, INFO, Fsw_01, Security violation: Login failure attempt via TELNET/SSH/RSH. IP Addr: 195.211.213.36
    """    
    def line_set(self):
        with open(self.fileName) as f:
            lineset=f.readlines()
        return lineset
    
    def errSnmpTrapSend(self,errDic):
        cfg=ConfigParser.RawConfigParser()
        cfgFile='config\\config.cfg'
        cfg.read(cfgFile)
#         print os.path.isfile(cfgFile)
        try:
            snmp_ip=cfg.get('server','snmp_ip')
        except:
            snmp_ip='localhost'
        
        print snmp_ip
        
        
        """
        -v 1.3.6.1.4.1.6485.901.0 STRING 1234567                            <== serial
        -v 1.3.6.1.4.1.6485.901.1 STRING 2019-02-26 02:02:01             <== event_date
        -v 1.3.6.1.4.1.6485.901.2 STRING 0x1234                              <== event_code
        -v 1.3.6.1.4.1.6485.901.3 STRING Warning                             <== severity
        -v 1.3.6.1.4.1.6485.901.4 STRING This is test message              <== desc
        -v 1.3.6.1.4.1.6485.901.5 STRING EMC                                 <== vendor
        -v 1.3.6.1.4.1.6485.901.6 STRING STG                                  <== device_type
        -v 1.3.6.1.4.1.6485.901.7 STRING realtime ssh                                  <== method
        -v 1.3.6.1.4.1.6485.901.8 STRING etc                                  <== etc
        """
        
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((snmp_ip, 162)),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.6485.901'),
                ).addVarBinds(
                    ('1.3.6.1.4.1.6485.901.0', OctetString(errDic['serial'])),
                    ('1.3.6.1.4.1.6485.901.1', OctetString(errDic['event_date'])),
                    ('1.3.6.1.4.1.6485.901.2', OctetString(errDic['event_code'])),
                    ('1.3.6.1.4.1.6485.901.3', OctetString(errDic['severity'])),
                    ('1.3.6.1.4.1.6485.901.4', OctetString(errDic['desc'])),
                    ('1.3.6.1.4.1.6485.901.5', OctetString(errDic['vendor'])),
                    ('1.3.6.1.4.1.6485.901.6', OctetString(errDic['device_type'])),
                    ('1.3.6.1.4.1.6485.901.7', OctetString(errDic['method'])),
                    ('1.3.6.1.4.1.6485.901.8', OctetString(errDic['etc'])),
                    
                )
            )
        )
        if errorIndication:
            print(errorIndication)
    
    def get_config_name(self):
        fname=os.path.basename(self.fileName).strip()
        
        timeconfig=os.path.join('config','{}.conf'.format(fname.split('_')[0]))
        return timeconfig
    
    def set_dtime(self,event_date):
        
        with open(self.config_name,'w') as f:
            f.write(event_date)

    def get_dtime(self):
        if not os.path.isfile(self.config_name):
            last_event_date = datetime.datetime.now() - datetime.timedelta(days= 1)
            last_event_date = last_event_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            with open(self.config_name,'r') as f:
                last_event_date=f.read()
        return last_event_date

    def main(self):
#         print self.lineset
#         print type(self.lineset)
        err_bit=False
        last_event_date=self.get_dtime()
        print 'LAST EVENT DATE :',last_event_date
        for i in range(len(self.lineset)):
            line=self.lineset[i]
            if '###***errdump***###' in line:
                err_bit=True
            if err_bit:
                line_st = line.split(',')
                if len(line_st) > 6:
                    
                    event_date=datetime.datetime.strptime(line_st[0],'%Y/%m/%d-%H:%M:%S')
                    event_date = event_date.strftime('%Y-%m-%d %H:%M:%S')
                    message_id=line_st[1].strip()
                    esn = line_st[2].strip()
                    audit_flag = line_st[3].strip()
                    severity= line_st[4].strip()
                    switch_name=line_st[5].strip()
                    message = line_st[6].strip()
                    event_msg='{} {} '.format(switch_name,message)
#                     print event_date,last_event_date,event_date > last_event_date
                    if event_date > last_event_date:
                        if 'Login' not in message:
                            print event_date,severity
                            print event_msg
                            """
                                    -v 1.3.6.1.4.1.6485.901.0 STRING 1234567                            <== serial
        -v 1.3.6.1.4.1.6485.901.1 STRING 2019-02-26 02:02:01             <== event_date
        -v 1.3.6.1.4.1.6485.901.2 STRING 0x1234                              <== event_code
        -v 1.3.6.1.4.1.6485.901.3 STRING Warning                             <== severity
        -v 1.3.6.1.4.1.6485.901.4 STRING This is test message              <== desc
        -v 1.3.6.1.4.1.6485.901.5 STRING EMC                                 <== vendor
        -v 1.3.6.1.4.1.6485.901.6 STRING STG                                  <== device_type
        -v 1.3.6.1.4.1.6485.901.7 STRING realtime ssh                                  <== method
        -v 1.3.6.1.4.1.6485.901.8 STRING etc                                  <== etc
        """
                            errDic={}
                            serial=self.fileName.split('_')[0]
                            errDic['serial'] = serial
                            errDic['event_date']=event_date
                            errDic['event_code'] = message_id
                            errDic['severity'] = severity
                            errDic['desc'] = message
                            errDic['vendor'] = 'Brocade'
                            errDic['device_type']='SWI'
                            errDic['method'] = 'realtime ssh'
                            errDic['etc'] = 'External sequence number : {} , securityu audit flag : {}'.format(esn,audit_flag)
                            self.errSnmpTrapSend(errDic)
                    
                
            if '###***portperfshow***###' in line:
                err_bit = False
        
        self.set_dtime(event_date)
            

if __name__=='__main__':
        fn=os.path.join('data','ALJ2503G08G_10.10.10.20.tmp')
        err_dump(fn).main()