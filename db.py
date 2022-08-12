import phoenixdb
import phoenixdb.cursor
import os
import random
#from apscheduler.schedulers.background import BackgroundScheduler

# import mysql.connector 
# from mysql.connector import Error

class Config:

    _cursor = None
    __connection = None
    __instance__ = None 
    #kinit first
    # os.system('export KRB5_CONFIG="/root/krb5.conf"')
    os.system('kinit -kt  /home/efan/.dbeaver-config/cldrodsdcsvc.keytab cldrodsdcsvc@HQ.BRI.CO.ID')

    
    
    def __init__(self) :
            try :
                server = ['hbdcm01.hq.bri.co.id', 'hbdcm02.hq.bri.co.id', 'hbdcm03.hq.bri.co.id']
                server = random.choice(server)
                # Config.__connection=phoenixdb.connect('http://hbdcm03.hq.bri.co.id:8765/',autocommit=True, auth="SPNEGO")
                Config.__connection=phoenixdb.connect('http://' +(server)+ ':8765/',autocommit=True, auth="SPNEGO")
                #Config.__connection = mysql.connector.connect(host='localhost', user='root', password='P@ssw0rd', db='classicmodels') 
            except:
                print("Error while connect to Phoenix") 
    #SINGLETON PATTERN
    # @staticmethod
    # def getInstance():
    #     if not Config.__instance__:
    #         Config()
    #     return Config.__instance__
    def kinit():
        os.system('kinit -kt /home/efan/.dbeaver-config/cldrodsdcsvc.keytab  cldrodsdcsvc@HQ.BRI.CO.ID')
        print("sukses kinit")
    #set schedule setiap 6 jam
    
    # sched = BackgroundScheduler(daemon=True)  
    # sched.add_job(kinit,'interval',hours=6)
    # sched.start()
    

    def cbalQuery(self,acctno) :
        query =f""" SELECT CBAL_BASE AS CBAL_BASE FROM REKENING_KORAN.DDMAST 
                WHERE ACCTNO = '{acctno}' """
                
        run = Config.run_query(self, query)
        return run

    #GEET DEMOGRAFI RECORD    
    def demografiQuery(self,acctno) :
        query =f"""
SELECT 
                ARRAY_TO_STRING(ARRAY[GELAR_SEBELUM_NAMA ,NAMA_LENGKAP,GELAR_SESUDAH_NAMA],' ') AS NAMA,
                ARRAY_TO_STRING(ARRAY[ALAMAT_ID1,ALAMAT_ID2,ALAMAT_ID3],' ') AS ALAMAT,
                current_date() AS TanggalLaporan,
                ACCTNO,
                RTRIM(e.JDNAME) AS UNIT_KERJA,ARRAY_TO_STRING(ARRAY[RTRIM(e.JDADDR) ,RTRIM(e.JDCSZ)],' ') AS ALAMAT_UNIT_KERJA,
                RTRIM(f.PSCDES) AS PRODUCT,
                f.DP2CUR AS VALUTA
            FROM  CHUB_DEMOGRAPHY c 
            JOIN 
            (SELECT 
                a.CIFNO,ACCTNO,a.BRANCH, a.SCCODE
            FROM REKENING_KORAN.DDMAST a
            WHERE a.ACCTNO ='{acctno}' LIMIT 1)   AS d         
            ON c.CIFNO = d.CIFNO
            LEFT JOIN REKENING_KORAN.JHDATA e
            ON d.BRANCH = e.JDBR
            LEFT JOIN REKENING_KORAN.AS4_DDPAR2 f
            ON d.SCCODE = f.SCCODE"""

        run = Config.run_query(self, query)
        return run


    def MutasiQuery(self, acctno, start_date, end_date) : 
        query = f"""    
                 SELECT 
                        dhist.TRACCT AS TRACCT
                        ,dhist.TRDATE  AS TRDATE
                        ,CASE 
                            WHEN dhist.TRDORC ='C' THEN dhist.amt
                            ELSE 0
                        END AS KREDIT
                        ,CASE	
                            WHEN dhist.TRDORC ='D' THEN dhist.amt 
                            ELSE 0
                        END AS DEBIT
                        ,REGEXP_REPLACE(TRUSER,' ',' ') as TRUSER
                        ,SUBSTR(REGEXP_REPLACE(LPAD(TRTIME,6),' ','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TRTIME,6),' ','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TRTIME,6),' ','0'),4,2) AS WAKTU
                        ,CASE
                        WHEN 
                        	TRREMK = '                                        ' AND TLBDS1 IS NULL AND TLBDS2 IS NULL   
                        	THEN RTRIM(DDPAR3.DESCRIPTION) 
						WHEN RTRIM(TRREMK) = RTRIM(TLBDS1)  THEN  ARRAY_TO_STRING(ARRAY[TRREMK ,TLBDS2],' ')
						WHEN RTRIM(TRREMK) = RTRIM(TLBDS2)  THEN  ARRAY_TO_STRING(ARRAY[TRREMK ,TLBDS1],' ')
						ELSE ARRAY_TO_STRING(ARRAY[TRREMK,TLBDS1,TLBDS2],' ')
						END AS REMARK 
                FROM REKENING_KORAN.DL_DDHIST dhist
                INNER JOIN REKENING_KORAN.AS4_DDPAR3 DDPAR3
                ON dhist.TRANCD = DDPAR3.TRANCD
                WHERE dhist.TRACCT = '{acctno}' AND TO_NUMBER(dhist.TRDATE) BETWEEN 2022150 AND 2022190
                ORDER BY (dhist.TRDATE,dhist.TRTIME) ASC""" 

        run = Config.run_query(self, query) 
        # for row in run :
        return run
    def sum_query(self, acctno,start_date, end_date):
        query=f"""select 
                      CASE WHEN TRDORC ='D' THEN sum(amt) END AS sum_debit
                     ,CASE WHEN TRDORC ='C' THEN SUM(amt) END AS sum_kredit 
                   from DL_DHIST WHERE TRACCT='{acctno}' group by TRDORC;"""
        run = Config.run_query(self, query)

    def dummy_query(self, acctno,start_date, end_date) :

        query = f""" 
            select 
                CBAL,
                 TRACCT 
                ,TRDATE
                ,CASE 
                    WHEN TRDORC ='C' THEN amt
                    ELSE 0
                END AS Kredit
                ,CASE	
                    WHEN TRDORC ='D' THEN amt 
                    ELSE 0
                END AS Debit
                ,TRTIME
                ,TRNCD
            from DL_DHIST a
            join DDMAST b on a.tracct = b.acctno and TRACCT = '{acctno}'"""

        run = Config.run_query(self, query)
        
        return run

    #Method to running Query
    def run_query(self,sql) :
        Config._cursor = Config.__connection.cursor()
        Config._cursor.execute(sql)
        
        return Config._cursor       