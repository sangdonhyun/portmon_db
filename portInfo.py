'''
Created on 2020. 2. 25.

@author: Administrator
'''
import fleta_dbms
import datetime
class PortInfo():
    def __init__(self):
        self.rdb=fleta_dbms.FletaDb()
        self.pdb=fleta_dbms.FpimDb
        self.yd=self.getYd()
        self.tbname=self.get_table()
    
    def getYd(self):
        td=datetime.datetime.now()
        yd=td+datetime.timedelta(days=-1)
        return yd
#         return yd.strftime('%Y_%m_%d')
    def get_table(self):
        tbname='perfom_swi.perform_swi_brocade_port_status_{}'.format(self.yd.strftime('%Y_%m_%d'))
        return tbname
    
    
    def get_swList(self):
        
        
        
#         print tbname
        query='select swi_serial from {} group by swi_serial'.format(self.tbname)
#         print query
        rows=self.rdb.getRaw(query)
        swList=[]
        for row in rows:
#             print row
            swList.append(row[0])
        
        return swList
    
    
    def get_PortInfo(self,sw_serial):
        query="select * from {} where swi_serial='{}' order by 1 desc limit 1".format(self.tbname,sw_serial)
#         print query
        port_rows=self.rdb.getRaw(query)
        portInfo= port_rows[-1][-1]
#         print portInfo
        num=portInfo.pop(0)
#         print len(portInfo)
#         print int(num)
#         print len(portInfo)%int(num)
        dnum= len(portInfo)/int(num)
        i=0
        portIndex={}
        for n in range(dnum):
            port= portInfo[i:i+dnum]
            if len(port) == dnum:
                portIndex[port[0]]=port[3]
            i=i+dnum
#         print portIndex
        return portIndex
            
        
    
    def main(self):
        sw_list=self.get_swList()
        for sw in sw_list:
            portIndex=self.get_PortInfo(sw)
            print portIndex
if __name__=='__main__':
    PortInfo().main()