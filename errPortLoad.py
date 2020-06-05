'''
Created on 2018. 11. 5.

@author: user
'''
import os
import re
import sys
import ConfigParser
import glob
import time
import portinfo_insert
from time import strftime, localtime, time

class Load():
    def __init__(self):
        self.portinfolist=[]
        self.portlist=[]
        
    
    
    
    def getPortNum(self,port):
        no = 0
        num = 0
        
        
        for portinfo in self.portinfolist:
           
            if int(portinfo['portindex']) == int(port):
                num = no
                break
            no = no +1
        return num
             
        
    
    def fread(self,file,store_time):
        
        portinfolist=[]
        portlist=[]
        crcBit,txBit,rxBit=False,False,False
        with open(file) as f:
            rd=f.read()

        
        lineset=rd.splitlines()
        
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
        for line in lineset :
            portinfo={}
            
            if  '#   EXECUTE DATE :' in line:
                event_time = ''.join(line.split('EXECUTE DATE :')[1:])
                event_time = event_time.replace('#','').strip()
                 
                 
            if  '#### DATA TIME :' in line:
                event_time = ''.join(line.split('EXECUTE DATE :')[1:])
                event_time = event_time.replace('#','').strip()
#                 
                
            
            if '###***chassisshow***###' in line:
                serialBit= True
            if serialBit:
                
                if 'Factory Serial Num:' in line:
                    
                    serial = line.split(':')[1].strip()
                    serialBit = False
                    
            
            
            
            if '###***' in line:
                crcBit,txBit,rxBit=False,False,False
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
                    portinfo['serial'] = serial
                    
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
                    if 'uWatts' not in line:
                        tx=line.split('(')[1].split(')')[0]
                        
                        tx=tx.replace('uW','')
                    else:
                        tx=line.split()[2]
                        
                    listnum=self.getPortNum(self.portlist[num-1])
                    
                    portinfo = self.portinfolist[listnum]
                    portinfo['tx'] = tx
                   
                    self.portinfolist[listnum] = portinfo
#                     crcerr = portinfolist[listnum]['crcerr']
#                     portinfolist[listnum] = {'num' : portlist[num],'tx' : tx,'crcerr' : crcerr }
                    
                    
                if 'RX Power:' in line:
#                     print slot,pnum,portlist[num]
#                     print line
                    if 'uWatts' not in line:
                        rx=line.split('(')[1].split(')')[0]
                        rx=rx.replace('uW','')
                    else:
                        #print line
                        rx=line.split()[2]
                        
                    
                    
                    
                    listnum=self.getPortNum( self.portlist[num-1])
                    
                    
                    portinfo = self.portinfolist[listnum]
                    
                    portinfo['rx'] = rx
                    self.portinfolist[listnum] = portinfo
        
                
        rtfile = os.path.join('ret''%s.tmp'%serial)
        
        resutllist=[]
        with open('result.txt','a') as f:
            for no in range(len(self.portinfolist)):
                
                portinfo = self.portinfolist[no]
                if 'slot' in portinfo.keys():
                    resutllist.append(portinfo)
        
                
                
                #f.write(str(portinfo)+'\n')
            #f.write(file)
        #print 'serial :',serial            
        
        #print len(self.portinfolist)
        #print file
        if event_time == '':
            event_time = store_time
        print 'store_time 1',store_time
        portinfo_insert.inst(resutllist,store_time,event_time)
        
        
    def main(self):
        print '#'*80
        print '#'*80
        print '#'*80
        store_time=strftime("%Y-%m-%d %H:%M:%S", localtime(time()))
        print 'stor_time 0 :',store_time
        flist=glob.glob('./data/*')
        for file in flist:
            #print 'FILE NAME:',file
            self.portinfolist=[]
            self.portlist=[]
            self.fread(file,store_time)
            
            #print '#'*80
            #print '#'*80
            #print '#'*80
                
                
if __name__=='__main__':
    Load().main()