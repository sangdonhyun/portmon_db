import os
import errno
import datetime
from netmiko import ConnectHandler
import ConfigParser
import common


 




class netmiko():
    def __init__(self,portInfo):
        self.portInfo=portInfo
        self.cfg=self.getCfg()
        self.cmdList=self.getCmdList()
        self.ip = portInfo['ip']
        print '03 :',portInfo.keys()
        self.name = portInfo['name']
        self.portInfo.pop('name')
        self.password=portInfo['password']
        self.username=portInfo['username']
        self.fileName=os.path.join('data','%s_%s.tmp'%(self.name,self.ip,))
        self.com=common.Common()
        self.net_connect = ConnectHandler(**self.portInfo)
    
    def run(self):

        net_connect = ConnectHandler(**self.portInfo)
        for cmd in self.cmdList:
            title='###***%s***###'%cmd
            self.fileWrite(title)
            output = net_connect.send_command(cmd)
            print output
            self.fileWrite(output)
        
        
        
        
    def getCfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        print cfgFile,os.path.isfile(cfgFile)
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
    def main(self):
        headmsg=self.com.get_module_head_msg(s_hostname=self.name,s_ip=self.ip)
        print headmsg
        self.fileWrite(headmsg, 'w')
        self.run()
#         self.expectCmd()
        endmsg = self.com.get_module_tail_msg()
        self.fileWrite(endmsg)
        

    def expectCmd(self):
        ret=self.net_connect.send_command_expect(
         "portperfshow 1",
         expect_string="Total",
         delay_factor=5,
        )
        self.fileWrite('###***portperfshow***###')
        print ret
        if type(ret) == 'unicode':
            self.fileWrite(ret.decode('utf-8'))
        else:
            self.fileWrite(ret)
            
         

if __name__=='__main__':
    portInfo={'username': 'admin', 'name': 'fsw01', 'ip': '121.170.193.209', 'secret': 'False', 'device_type': 'brocade_nos', 'password': 'password', 'port': '20001', 'verbose': 'False'}
    print portInfo
    netmiko(portInfo).main()
