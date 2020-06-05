'''
Created on 2019. 12. 6.

@author: user
'''
import redis
import time
import datetime
import fleta_dbms
from ConfigParser import ConfigParser
print 'redis '

class Avg():
    def __init__(self):
        self.serial=''
        # r=redis.Redis(host='121.170.193.222', port=6379)
        self.r = redis.StrictRedis(host="121.170.193.222", port=6379, db=0, password='kes2719!')
        # redis_db.lpush('test','1,2,3,4,5')

        self.now=datetime.datetime.now().strftime('%Y-%m-%d %H')
        self.hour=self.now[-1:-2]
        self.rangemin=''
        self.portnumList=None
        self.rdb=fleta_dbms.FletaDb()
        self.pdb=fleta_dbms.FpimDb()
        
    
        
    
    def getAvg(self,datehour,target):
        portVal={}
        """
        lrange "brocade_latest_time_000000000ALJ2503G08G_2019-12-09 10" 0 -1
        
        b121.170.193.222:6379> keys "2019-12-06 13:04:34::000000000ALJ2503G08G:*"
        1) "2019-12-06 13:04:34::000000000ALJ2503G08G::SFP_RX_POWOR::uWatts"
        2) "2019-12-06 13:04:34::000000000ALJ2503G08G::CRC::count"
        3) "2019-12-06 13:04:34::000000000ALJ2503G08G::throughput::byte"
        4) "2019-12-06 13:04:34::000000000ALJ2503G08G::SFP_TX_POWOR::uWatts"
        """
        lastkey='brocade_latest_time_{}_{}'.format(self.serial,datehour)
        print lastkey
#         serial=lastkey.split('_')[3]
        timelist= self.r.lrange(lastkey, 0, -1)
        print timelist
        
        htot,mtot=0,0
        timelist
        rangeMinList=[]
        
        for mtime in timelist:

#             print mtime
            key='{}::{}::{}'.format(mtime,self.serial,target)
            txInfo= self.r.hgetall(key)
            
            keys=txInfo.keys()
            print keys
            print self.portnumList
            if self.portnumList == [] or self.portnumList==None:
                self.portnumList=keys
            print self.portnumList
            vals=txInfo.values()
            rangemin=mtime[:-3]
            datemin=mtime[:-3]
            
            print self.portnumList
                
            for i in range(len(vals)):
                val=vals[i]
                portnum=self.portnumList[i]
                if portnum not in portVal.keys():
                    portVal[portnum] = []  
                portVal[portnum] = portVal[portnum]+[((mtime,float(val)))]
                htot=htot+1
        print 'htot :',htot
        
        return portVal
        
    def main(self):
        """
        1) "SFP_TX_POWOR"
2) "SFP_RX_POWOR"
3) "CRC"
4) "throughput"
        """
        
        while True:
            dnow=datetime.datetime.now().strftime('%Y-%m-%d %H')
            if not dnow==self.now:
                flagList=self.getFlagList()
                for flag in flagList:
                    self.run(flag)
            self.now=dnow
            time.sleep(60)
    def minAvg(self,minInfoList,target,portnum):
        
        for minInfo in minInfoList:
            keys=minInfo.keys()
            vals=minInfo.values()
            if len(vals) > 0:
                val_avg= sum(vals,0.0)/len(vals)
                val_max= max(vals)
                val_max_index = vals.index(val_max)
                val_max_date=keys[val_max_index]
                val_min= min(vals)
                val_min_index = vals.index(val_min)
                val_min_date=keys[val_min_index]
                mdate= keys[0][:-1]+'0'
                """
                ins_date, check_date, device_type, flag_1, 
               cols_max_date, cols_value_max, cols_value_avg, mdb_key
               
                """
                minDic={}
                minDic['ins_date'] = mdate[:10]
                minDic['check_date'] = mdate [:15]+'0'
                minDic['device_type'] = 'brocade'
                minDic['flag_1'] = self.serial
                minDic['flag_2'] = target
                minDic['flag_3'] = ''
                minDic['flag_4'] = portnum
                minDic['cols_max_date'] = val_max_date[-8:]
                minDic['cols_value_max'] = val_max
                minDic['cols_value_avg'] = val_avg
                minDic['mdb_key'] = '{}::{}'.format(self.serial,target)
                self.pdb.dbInsert(minDic, 'monitor.perform_stg')
    #         return mdate,val_avg,val_max,val_max_index,val_max_date,val_min,val_min_index,val_min_date
    
    def getFlagList(self):
        flagList=self.r.lrange('brocade_flag_list',0,-1)
        return  flagList
    
    
    
    def redis_set(self):
        self.r.lrange('brocade_device_list',0,-1)
        device_set=self.r.lrange('brocade_device_list',0,-1)
        print device_set
        for serial in device_set:
            self.serial = serial
            print '*'*50
            flagList=self.getFlagList()
            print flagList
            for flag in flagList:
                print flag
                self.run(flag)
            
            
    def run(self,flag):
        
        
        check_date=datetime.datetime.now() - datetime.timedelta(hours=1)
        check_date= check_date.strftime('%Y-%m-%d %H')
        print check_date
        portVal= self.getAvg(check_date,flag)
        
        print portVal
        
        portnumlist=portVal.keys()
        minInfo0,minInfo1,minInfo2,minInfo3,minInfo4,minInfo5={},{},{},{},{},{}
        for i in range(len(portVal.values())):
            val_avg,val_max,val_min,val_max_date,val_min_date = None,None,None,None,None
            keys,vals=[],[]
            portnum = portnumlist[i]
#             print 'PORT Index :',portnum
            portDevVal= portVal[portnum]
#             print portDevVal
            for j in range(len(portDevVal)):
                
                key,val=portDevVal[j]
                minchr=key[14:15]
                if minchr=='0':
                    minInfo0[key]=val
                elif minchr=='1':
                    minInfo1[key]=val
                elif minchr=='2':
                    minInfo2[key]=val
                elif minchr=='3':
                    minInfo3[key]=val
                elif minchr=='4':
                    minInfo4[key]=val
                elif minchr=='5':
                    minInfo5[key]=val
                else:
                    pass
                
                keys.append(key)
                vals.append(val)
            val_avg= round(sum(vals,0.0)/len(vals),2)
            val_max= round(max(vals),2)
            val_max_index = vals.index(val_max)
            val_max_date=keys[val_max_index]
            val_min= round(min(vals),2)
            val_min_index = vals.index(val_min)
            val_min_date=keys[val_min_index]
            
            """
            ins_date, check_date, device_type, flag_1, flag_2,  flag_3,  flag_4,  
            cols_max_date, cols_value_max, cols_value_avg, mdb_key
            """
            
#             print check_date,portnum,val_avg,val_max,val_min,val_max_date,val_min_date
#             print minInfo0
            hourDic={}
            hourDic['ins_date'] = check_date[:10]
            hourDic['check_date'] = check_date[:13]
            hourDic['device_type'] = 'brocade'
            hourDic['flag_1'] = self.serial
            hourDic['flag_2'] = flag
            hourDic['flag_3'] = ''
            hourDic['flag_4'] = portnum
            hourDic['cols_max_date']  =val_max_date[-8:]
            hourDic['cols_value_max'] = val_max
            hourDic['cols_value_avg']  = val_avg
            hourDic['mdb_key'] = '{}::{}'.format(self.serial,flag)
            print hourDic
            self.pdb.dbInsert(hourDic, 'monitor.perform_stg')
            minInfoList=[minInfo0,minInfo1,minInfo2,minInfo3,minInfo4,minInfo5]
            self.minAvg(minInfoList,flag,portnum)
            
            
if __name__=='__main__':
    
    
    Avg().redis_set()
    