'''
Created on 2018. 11. 21.

@author: user
'''
import sys, paramiko
import time
import ConfigParser
import os
from time import strftime
import common

now = strftime("%y%m%d-%H%M%S")
start_time = time.time() 
print now
# 
# hostname='121.170.193.209'
# username='root'
# password='fleta0901!'
# port =22
# 
# 
# cmd1='uname -a'
# cmd2='cat /etc/passwd'
# try:
#     
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 
# 
#     
#     
#     client.connect(hostname, port=port, username=username, password=password)
# 
#     stdin, stdout, stderr = client.exec_command(cmd1)
#     print stdout.read(),
#     
#     stdin, stdout, stderr = client.exec_command(cmd2)
# 
# finally:
#     client.close()
#     
#     
# hostname='121.170.193.215'
# username='root'
# password='fleta0901!'
# port =22
# 
# 
# cmd1='uname -a'
# cmd2='cat /etc/passwd'
    



class Paramiko():
    def __init__(self,portInfo):
        self.cfg=self.getCfg()
        self.cmdList=self.getCmdList()
        self.ip = portInfo['ip']
        self.name = portInfo['name']
        self.password=portInfo['password']
        self.username=portInfo['username']
        self.port=portInfo['port']
        self.fileName=os.path.join('data','%s_%s.tmp'%(self.name,self.ip,))
        self.com=common.Common()
        
        
    def getCfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        print cfgFile,os.path.isfile(cfgFile)
        cfg.read(cfgFile)
        return cfg
        
    def getCmdList(self):
        cmdList=[]
        for cmdno in sorted(set(self.cfg.options('command'))):
            cmd=self.cfg.get('command',cmdno)
            cmdList.append(cmd)
        
        return cmdList
    
    def run(self):
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.ip, username=self.username, password=self.password,port=self.port)
        
            for cmd in self.cmdList:
                title='###***%s***###'%cmd+'\n'
                self.fileWrite(title)
                
                stdin, stdout, stderr = client.exec_command(cmd)
                self.fileWrite(str(stdout.read()))
                
        finally:
            client.close()
        
    
    def fileWrite(self,msg,wbit='a'):
        with open(self.fileName,wbit) as f:
            f.write(msg+'\n')
         
    def main(self):
        
        headmsg=self.com.get_module_head_msg(s_hostname=self.name,s_ip=self.ip)
        print headmsg
        self.fileWrite(headmsg, 'w')
        self.run()
        endmsg = self.com.get_module_tail_msg()
        self.fileWrite(endmsg)
        

if __name__=='__main__':
    portInfo={'username': 'root', 'name': 'hostname', 'ip': '121.170.193.209', 'secret': 'False', 'device_type': 'ovs_linux', 'password': 'fleta0901!', 'port': '22', 'verbose': 'False'}
    Paramiko(portInfo).main()


    
    
    
    
        
        
