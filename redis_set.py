'''
Created on 2019. 11. 18.

@author: user
'''

import redis
import fleta_dbms

r = redis.StrictRedis(host="121.170.193.222", port=6379, password='kes2719!')

"""
['unity', 'isilon', 'brocade', 'netapp']
['000000000ALJ2503G08G', '000000000ALJ0602F04S']
['SFP_TX_POWER', 'SFP_RX_POWER', 'CRC', 'throughput']
{'real': 'device::flag'}

"""
type_list= r.lrange('type_list',0,-1)
print "TYPE LIST :" ,type_list
if 'brocade' not in type_list:
    r.rpush('type_list','brocade')
 
l_dev_list=['000000000ALJ2503G08G', '000000000ALJ0602F04S']
r_dev_list= r.lrange('brocade_device_list',0,-1)
 
for dev in l_dev_list:
    print 'DEVICE :',dev
    if dev not in r_dev_list:
        r.rpush('brocade_device_list',dev)
 
         
 
print r.hgetall("brocade_key_format")
 
l_flag_list=['SFP_TX_POWER', 'SFP_RX_POWER', 'CRC', 'throughput']
r_flag_list= r.lrange('brocade_flag_list',0,-1)
 
for flag in l_flag_list:
    if flag not in r_flag_list:
        r.rpush('brocade_flag_list',flag)
         
brocade_key_format={'real': 'device::flag'}

key_format= r.hgetall('brocade_key_format')
if key_format == {}:
    r.hset('brocade_key_format','real','device::flag')



# rdb=fleta_dbms.FletaDb()

# query_string='select * from '
# dev_list=rdb.getRaw(query_string)

