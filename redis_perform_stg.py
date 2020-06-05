'''
Created on 2019. 12. 12.

@author: user
'''
import datetime
import os
import time
import redis_brocade
# import redis_unity
# import redis_netapp

olddate=datetime.datetime.now().strftime('%Y:%m:%d %H')


print 'DATE' ,olddate
while True:
    newdate=datetime.datetime.now().strftime('%Y:%m:%d %H')
    if newdate != olddate:
        try:
            redis_brocade.Avg().redis_set()
        except:
            pass
#         try:
#             redis_unity.Avg().redis_set()
#         except:
#             pass
#         try:
#             redis_netapp.Avg().redis_set()
#         except:
#             pass
#         try:
#             redis_isilon.Avg().redis_set()
#         except:
#             pass
        print 'DATE CHANGE :',olddate,newdate 
        olddate=newdate
    time.sleep(60*5)




