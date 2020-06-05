'''
Created on 2020. 2. 17.

@author: Administrator
'''
import os
import fleta_dbms
import ConfigParser
import datetime
class list_to_rdb():
    def __init__(self):
        self.rdb=fleta_dbms.FletaDb()
        
    def getList(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        swList=[]
        for sec in cfg.sections():
            swInfo={}
            swInfo['name']=sec
            for opt in cfg.options(sec):
                swInfo[opt] = cfg.get(sec,opt)
            swList.append(swInfo)
        return swList
    
    def get_ori_serial(self,serial):
        
        query_str="SELECT swi_serial, chk_swi_serial FROM live.live_swi_brocade_serial_info where chk_swi_serial='{}'".format(serial)
        print query_str
        rows=self.rdb.getRaw(query_str)
        
        for row in rows:
            serial = row[0]
            
        return serial
        
    def main(self):
        print self.getList()
        ndate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for swInfo in self.getList():
            
            serial = self.get_ori_serial(swInfo['name'])
            print serial
            query="""INSERT INTO ref.ref_code_san_info(
            swi_serial, create_date, device_type, 
            create_ip, user_name, pass_word, port, 
            secret, verboses, 
            event_snmp, event_log, crc, sfp, throughput, 
            interval_time)
    VALUES ('{}', '{}', '{}', 
            '{}', '{}','{}','{}', 
            '{}','{}',
            '{}','{}','{}','{}','{}',
            '{}'
            );

            """.format(
            serial,ndate,swInfo['device_type'],
            swInfo['ip'],swInfo['username'],swInfo['password'],swInfo['port'],
            swInfo['secret'],swInfo['verbose'],
            'O', 'O', 'O', 'O', 'O', 
            '10'
                )
            print query
            
            self.rdb.queryExec(query)

if __name__=='__main__':
    list_to_rdb().main()
