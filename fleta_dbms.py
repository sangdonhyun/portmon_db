# -*- encoding:cp949*-    
'''
Created on 2013. 2. 11.

@author: Administrator
'''

import sys
import os
import psycopg2
import ConfigParser
import codecs
import locale
import common


class FpimDb():
    def __init__(self):
        self.cfg = self.getCfg()
        self.conn_string = self.getConnStr()
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    def getConnStr(self):
        ip = self.cfg.get('fpim_db','ip')
        dbname = self.cfg.get('fpim_db','dbname')
        user = self.cfg.get('fpim_db','user')
        passwd = self.cfg.get('fpim_db','password')
        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd)
    
    def dbInsert(self,dic,table='monotir.pm_auto_isilon_info'):
        
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
#         print query
#         self.qwrite(query)
        con = None
         
        try:
              
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
#                         
            cur.execute(query)
            con.commit()
             
#             print "Number of rows updated: %d" % cur.rowcount
                
         
        except psycopg2.DatabaseError, e:
             
            if con:
                con.rollback()
             
            print 'Error %s' % e    
            sys.exit(1)
             
             
        finally:
             
            if con:
                con.close()
    
class FletaDb():
    def __init__(self):
#         self.com = common.Common()
#         self.dec = common.Decode()
#         self.logger = self.com.flog()
                
#         self.conn_string = "host='localhost' dbname='fleta' user='fletaAdmin' password='kes2719!'"
        self.conn_string = self.getConnStr()
#         print self.conn_string
        self.cfg = self.getCfg()
        
        
    
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getConnStr(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        try:
            ip = cfg.get('database','ip')
        except:
            ip = 'localhost'
        try:
            user = cfg.get('database','user')
        except:
            user = 'webuser'
        try:
            dbname = cfg.get('database','dbname')
        except:
            dbname = 'qweb'
        try: 
            passwd = cfg.get('database','password')
        except:
            passwd = 'kes2719!'
        
        
        if len(passwd)>20:
            try:
                passwd= self.dec.fdec(passwd)
            except:
                pass
        
        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd)
        
    
    def getConnectInfo(self):
        dbinfo = {}
        for info in self.cfg.options('database'):
            val = self.cfg.get('database',info)
            if (info == 'passwd' or info == 'user') and len(val) >20:
                val - self.dec.fdec(val)
            dbinfo[info] = val
        return dbinfo
    
    def getNow(self):
        return self.com.getNow('%Y%m%d%H%M%S')
    
    
    def getHistMonth(self):
        return self.com.getNow('%Y%m%d')
    
    def queryExec(self,query):
        con = None
        try:
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            
            cur.execute(query)
            con.commit()
#             print "Number of rows updated: %d" % cur.rowcount
        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
            print 'Error %s' % e    
            sys.exit(1)
        finally:
            if con:
                con.close()

    

    def isEvnt(self,query):
    
        db=psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        print 'query 2:',query
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows == None:
            self.com.sysOut('Empty result set from query')
        
                
        cursor.close()
        db.close()
        return rows[0]
    
    def evtInsert(self,insquery):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            
            cur.execute(insquery)
            con.commit()
            
#             print "Number of rows updated: %d" % cur.rowcount
               
        
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()

    def qwrite(self,msg,wbit='a'):
        with open('query.txt',wbit) as f:
            f.write(msg+'굍굈')
    
    def isilonQuery(self,dic,table='monotir.pm_auto_isilon_info'):
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
#         print query
        return query
        
    
    
    def getQList(self,dicList,table='monotir.pm_auto_isilon_info'):
        qList=[]
        for dic in dicList:
            colList= dic.keys()
            valList= dic.values()
            colStr = '('
            for i in colList:
                colStr += "%s"%i +','
            if colStr[-1]==',':
                colStr = colStr[:-1]+')'
            val = ()
            for i in valList:
                
                val+=(i,)
            valStr = str(val)
            query = 'insert into %s %s values %s;'%(table,colStr,valStr)
            qList.append(query)
        return qList
#         print query
    
    
    def dbInsertDicList(self,dicList,table='monotir.pm_auto_isilon_info'):
        qList=self.getQList(dicList, table)
        con = None
        
        
        
        try:
              
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            for q in qList:
                
                cur.execute(q)
            con.commit()
             
#             print "Number of rows updated: %d" % cur.rowcount
                
         
        except psycopg2.DatabaseError, e:
             
            if con:
                con.rollback()
             
            print 'Error %s' % e    
            sys.exit(1)
             
             
        finally:
             
            if con:
                con.close()
        
            
    
    
    def dbInsert(self,dic,table='monotir.pm_auto_isilon_info'):
        
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
#         print query
        self.qwrite(query)
        con = None
         
        try:
              
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
#                         
            cur.execute(query)
            con.commit()
             
#             print "Number of rows updated: %d" % cur.rowcount
                
         
        except psycopg2.DatabaseError, e:
             
            if con:
                con.rollback()
             
            print 'Error %s' % e    
            sys.exit(1)
             
             
        finally:
             
            if con:
                con.close()
    
    def dbQeuryIns(self,query):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
#             sys.exit(1)
        finally:
            
            if con:
                con.close()

    
    def getQuery(self):
        queryfile = os.path.join(self.com.confDir,'query.txt')
        if not os.path.isfile(queryfile):
            with open(queryfile,'w') as f:
                f.write('''
select     ctrl_unum,
    ctrl_alias,
    pool_id,     -- pool name
    alloc_rate,  
    pool_alloc_rate, 
    round(dp_free_capacity/1024) free_capacity  -- free space GB
from (
    select     kk1.*,
        COALESCE(dp_free_capacity,0) dp_free_capacity,
        pool_capacity-COALESCE(dp_free_capacity,0) pool_alloc_capacity,
        dp_capacity - dp_used_capacity ddp_free_capacity,
         case when COALESCE(pool_capacity,0)-COALESCE(dp_capacity,0) < 0 
       then 0 
       else COALESCE(pool_capacity,0)-COALESCE(dp_capacity,0)
       end   unused_pool_capacity,
        case when pool_capacity = 0 then 0 else round(((pool_capacity-COALESCE(dp_free_capacity,0))/pool_capacity)*100) end pool_alloc_rate,
        ctrl_alias
    from (
        select     kk1.*,
            dp_count,
            dp_capacity,
            dp_used_capacity,
            pool_capacity-dp_capacity pool_free_capacity,
            round((dp_capacity/pool_capacity)*100) alloc_rate
            
            from (
            select ctrl_unum,SUBSTR((xmlagg((',' || raid_type)::xml))::text,2) raid_type,
                 SUBSTR((xmlagg((',' || pool_count)::xml))::text,2) pool_count2,
                 SUBSTR((xmlagg((',' || pool_capacity)::xml))::text,2) pool_capacity2,
                 sum(pool_capacity) pool_capacity,
                 sum(pool_count) pool_count,
                 pool_id
            from( 
                select ctrl_unum,raid_type,sh_target_ctrl pool_id,count(*) pool_count,sum(head_lun_size) pool_capacity,round(sum(head_lun_size)/1024) pool_capacity2
                FROM fs_auto_ldev_info 
                where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') 
                and (vg_name = 'HDP' or vg_name = 'V-VOL')
                group by ctrl_unum,sh_target_ctrl,raid_type
                union all 
                select ctrl_unum,raid_type,replace(drive_unique,'MID.',''),0,usable_capacity,usable_capacity
                from fs_auto_smr_raid 
                where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') 
                and strpos(drive_unique,'ID.') > 0  

                union all 
                select ctrl_unum,raid_type,replace(drive_unique,'CX_',''),0,usable_capacity,usable_capacity
                from fs_auto_smr_raid 
                where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') 
                and drive_unique like 'CX_%'

            
                union all
                select ctrl_unum,raid_type,pool_id,count(*) pool_count,sum(head_lun_size) pool_capacity,round(sum(head_lun_size)/1024) pool_capacity2
                from (
                    select kk1.ctrl_unum,kk1.raid_type,replace(kk2.raid_type,'EMC.PDEV.','') pool_id,drive_unum,count(*) hdd_count,head_lun_size 
                    from (
                        select *
                        from fs_auto_drive_info 
                        where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM')
                        and made_by_co = 'EMC'
                    )kk1 left outer join (    
                        select *
                        from fs_auto_ldev_info 
                        where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') and raid_type like 'EMC.PDEV%' 
                    )kk2 on kk1.ctrl_unum = kk2.ctrl_unum and drive_unum = lun_unum
                    where kk2.ctrl_unum is not null    
                    group by kk1.ctrl_unum,kk1.raid_type,kk2.raid_type,drive_unum,head_lun_size
                )kk group by ctrl_unum,raid_type,pool_id

            )aaa group by ctrl_unum,pool_id    
        )kk1 left outer join (    
            SELECT ctrl_unum,sh_target_ctrl dp_id,count(*) dp_count,sum(head_lun_size) dp_capacity,sum(pd_capacity) dp_used_capacity
            FROM fs_auto_ldev_info 
            where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') and array_group_nm not like 'CX_%' 
            and (array_group_nm like 'X%' OR array_group_nm like 'V%' or raid_type = 'RAID-V') 
            group by ctrl_unum,sh_target_ctrl

            union all
                
            SELECT ctrl_unum,replace(raid_type,'EMC.TDEV.','') dp_id,count(*) dp_count,sum(head_lun_size) dp_capacity,sum(pd_capacity) dp_used_capacity
            FROM fs_auto_ldev_info 
            where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM')  and raid_type like 'EMC.TDEV%' 
            group by ctrl_unum,raid_type

            union all
            
            SELECT ctrl_unum,replace(array_group_nm,'CX_','') dp_id,count(*) dp_count,sum(head_lun_size) dp_capacity,sum(pd_capacity) dp_used_capacity
            FROM fs_auto_ldev_info 
            where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') and array_group_nm like 'CX_%' 
            group by ctrl_unum,array_group_nm
            
        )kk2 on kk1.pool_id = kk2.dp_id     and kk1.ctrl_unum = kk2.ctrl_unum


    )kk1 left outer join (    
        select kk1.*,COALESCE(ctrl_alias,kk1.ctrl_unum) ctrl_alias
        from (
            SELECT substr(ctrl_unum,length(ctrl_unum)-4) ctrl_unum,temp_2 dp_id,round(sum(to_number(temp_3,'9999999999999.0'))) dp_free_capacity
            FROM fs_auto_hitach_info 
            where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM') and temp_1 = 'HDP'
            group by ctrl_unum,temp_2
        )kk1 left outer join (    
            select substr(ctrl_unum,length(ctrl_unum)-4) ctrl_unum,ctrl_alias
            from fs_man_ctrl_mst
            where hist_month = TO_CHAR(CURRENT_TIMESTAMP,'YYYYMM')
        )kk2  on kk1.ctrl_unum = kk2.ctrl_unum    
        
    )kk2 on kk1.pool_id = kk2.dp_id    and kk1.ctrl_unum = kk2.ctrl_unum
)aaaa    
order by 4 desc

                
                ''')
            
        with open(queryfile) as f:
            tmp = f.read()
        
        return tmp
    
    def eventList(self):
        db=psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        
        query_string = self.getQuery()
        cursor.execute(query_string)
        rows = cursor.fetchall()
        
        if rows == None:
            self.com.sysOut('Empty result set from query')
        
                
        cursor.close()
        db.close()
        return rows
    
    def getRaw(self,query_string):
        db=psycopg2.connect(self.conn_string)
        
        try:
            cursor = db.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
        
            
            cursor.close()
            db.close()
            
            return rows
        except:
            return []
    
    def insMany(self,insList,table):
        
        insdics = tuple(insList)
        db=psycopg2.connect(self.conn_string)
        
        try:
            cursor = db.cursor()
            query="""INSERT INTO monitor.%s (check_date, ctrl_unum, flag_nm, cols_nm, cols_value) VALUES (%s, %s, %s, %s, %s);"""%table
            cursor.executemany(query, insdics)
            
            db.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if db is not None:
                db.close()
    
    def isEvtByQeury(self,query):
       
       
        conn = None
        try:
             
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            
        except:
            print "I am unable to connect to the database."
        
        # If we are accessing the rows via column name instead of position we 
        # need to add the arguments to conn.cursor.
        
#         cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            cur.execute(query)
        except:
            pass
        #
        # Note that below we are accessing the row via the column name.
        try:
            rows = cur.fetchall()
    
            if rows[0][0] == 0:
                return True
            else:
                return False
        except:
            pass

if __name__ == '__main__':
    query  = """        SELECT check_date, cluster_nm, flag_nm, vol_nm_a, vol_nm_b, cols_nm, 
            cols_value
          FROM monitor.pm_keep_isilon_info where flag_nm ='ISI' and cols_value not in  ('OK' ,'n/a*','n/a')
          and check_date > '2016-06-02 15:21:40'"""
    query="select * from pg_tables where tablename = 'perform_stg_y2019m12d25' and schemaname ='monitor'"
    print FletaDb().getRaw(query)
    
    
        