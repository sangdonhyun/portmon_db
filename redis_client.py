'''
Created on 2019. 11. 18.

@author: user
'''
import redis
import time


print 'redis '
# r=redis.Redis(host='121.170.193.222', port=6379)
r = redis.StrictRedis(host="121.170.193.222", port=6379, db=0, password='kes2719!')
# redis_db.lpush('test','1,2,3,4,5')

print r.keys('brocade_latest_time_000000000ALJ2503G08G')



"""
SAN_SWITCH_LASTKEY::ALJ0602F04S
2019-11-18 19:09:18::SAN_SWICH_PERFROM::ALJ0602F04S
"""



