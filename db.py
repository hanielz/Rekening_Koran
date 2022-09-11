import phoenixdb
import phoenixdb.cursor
import os
import random
from datetime import timedelta
import datetime
from requests_gssapi import HTTPSPNEGOAuth
import database
from kerberos import kinit

#from apscheduler.schedulers.background import BackgroundScheduler

# import mysql.connector 
# from mysql.connector import Error


class Config():

    _cursor = None
    __connection = None
    __instance__ = None 

   
    kinit()

    def __init__(self) :
        try :
            conn = database.phoenix_connection_kerberos()
            randomconn = conn[random.randint(0,len(conn))]

            Config.__connection=randomconn
            Config._cursor=randomconn.cursor(cursor_factory=phoenixdb.cursor.DictCursor)
        except:
            print("Error while connect to Phoenix")


    def cbalQuery(self,acctno,start_date,con) :
        yesterday = Config.toDate(self, start_date) #convert to yesterday

        #JIKA PERIODE = END_OF_MONTH 
        query1 =f""" SELECT CBAL AS CBAL_BASE FROM REKENING_KORAN.AS400_DDMAST_{start_date[0:6]} 
                    WHERE ACCTNO = {acctno} """

        #JIKA PERIODE = DI HARI DAN BULAN YG SAMA
        query2 =f""" SELECT CBAL AS CBAL_BASE FROM REKENING_KORAN.AS400_DDMAST
                WHERE ACCTNO = {acctno} and PERIODE = {yesterday}"""

        if con == 1 : 
            run = Config.run_query(self, query1)
            return run
        if con == 2 :
            run = Config.run_query(self, query2)
            return run
        else :
            return False

    def cbalQueryLoan(self,acctno,start_date) :
        query = f"""sELECT cbal FROM REKENING_KORAN.AS400_LNMAST 
                    WHERE ACCTNO = {acctno} AND 
                        PERIODE = {start_date}"""
        run = Config.run_query(self, query)
        return run

    #GET GET TRANCD
    def trancdQuery(self,trancd) : 
        query =f"""SELECT trancd FROM REKENING_KORAN.AS4_DDPAR3 WHERE EFTTYP IN ('AFT','AGF')
                    AND trancd IN( '{trancd}' )"""

        run = Config.run_query(self,query)

        # result = []
        for row in run :
            # temp = row[0]
            # # temp['TRANCD'] = row[0]
            # result.append(temp)
            return row[0]

    #GET TLTXDS
    def tltxdsQuery(self, auxtrc) :
        query = f"""SELECT TLTXDS FROM REKENING_KORAN.AS400_TLTX 
                        WHERE TLTXCD={auxtrc}"""            
        run = Config.run_query(self,query)
        # return run
        for row in run :
            return row[0]
    
    #GET TLXAFT
    def tltxaftQuery(self, auxtrc) :
        query = f"""SELECT TLXAFT FROM REKENING_KORAN.AS400_TLTX 
                        WHERE TLTXCD={auxtrc}"""            
        run = Config.run_query(self,query)
        # return run
        for row in run :
            return row[0]

    #GET DDPAR3
    def descDdpar3Query(self,trancd) :
        query=f"""select a."DESC" FROM REKENING_KORAN.AS400_DDPAR3 a WHERE a.TRANCD = {trancd}"""

        run = Config.run_query(self,query)
        # return run
        for row in run :
            return row[0]



    #GET DEMOGRAFI RECORD :
    # 1. CASA    
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
            FROM REKENING_KORAN.AS400_DDMAST  a
            WHERE a.ACCTNO ={acctno} LIMIT 1)   AS d         
            ON c.CIFNO = d.CIFNO
            LEFT JOIN REKENING_KORAN.AS400_JHDATA  e
            ON d.BRANCH = e.JDBR
            LEFT JOIN REKENING_KORAN.AS4_DDPAR2 f
            ON d.SCCODE = f.SCCODE"""

        run = Config.run_query(self, query)
        return run


    def casaMutasiQuery(self, acctno, start_date, end_date,con) : 
         #CONVERT JULIAN DATE
        start_date = Config.convertJulianDate(start_date)
        end_date = Config.convertJulianDate(end_date)

        query1=f"""
            SELECT 
            	TRANCD AS TRANCD
                ,TRREMK AS TRREMK
                ,TRACCT AS TRACCT
                ,TRDATE  AS TRDATE
                ,AUXTRC 
            ,CASE 
                WHEN DORC ='C' THEN amt
                ELSE 0
                END AS KREDIT
                ,CASE	
                WHEN DORC ='D' THEN amt 
                ELSE 0
            END AS DEBIT, TRUSER ,SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),4,2) AS WAKTU
            ,TRREMK AS REMARK FROM REKENING_KORAN.AS400_DDTRN2  WHERE TRACCT  = {acctno} AND TRDATE = {end_date}
            ORDER BY (TRDATE,TIMENT) ASC"""

        query2 = f"""
            SELECT AUXTRC,TRANCD,TRACCT,TRDATE,KREDIT,DEBIT,TRUSER,WAKTU,TRREMK,REMARK FROM (
                    SELECT 
                        dhist.AUXTRC as AUXTRC
                        ,dhist.TRANCD AS TRANCD
                        ,dhist.TRACCT AS TRACCT
                        ,dhist.TRDATE  AS TRDATE
                        ,CASE WHEN dhist.TRDORC ='C' THEN dhist.amt ELSE 0 END AS KREDIT
                        ,CASE WHEN dhist.TRDORC ='D' THEN dhist.amt ELSE 0 END AS DEBIT
                        ,REGEXP_REPLACE(dhist.TRUSER,' ',' ') as TRUSER
                        ,SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TRTIME),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TRTIME),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TRTIME),7),' |,','0'),4,2) AS WAKTU
                        ,dhist.TRREMK
                        ,CASE 
                            WHEN TRREMK = '                                        ' AND dhist.TLBDS1 IS NULL AND dhist.TLBDS2 IS NULL THEN RTRIM(DDPAR3."DESC") 
                            WHEN RTRIM(dhist.TRREMK) = RTRIM(dhist.TLBDS1)  THEN  ARRAY_TO_STRING(ARRAY[dhist.TRREMK ,dhist.TLBDS2],' ')
                            WHEN RTRIM(dhist.TRREMK) = RTRIM(dhist.TLBDS2)  THEN  ARRAY_TO_STRING(ARRAY[dhist.TRREMK ,dhist.TLBDS1],' ')
                                ELSE ARRAY_TO_STRING(ARRAY[dhist.TRREMK,dhist.TLBDS1,dhist.TLBDS2],' ')
                        END AS REMARK 
                    FROM REKENING_KORAN.AS400_DDDHIS dhist
                    LEFT JOIN REKENING_KORAN.AS400_DDPAR3 DDPAR3
                    ON dhist.TRANCD = DDPAR3.TRANCD
                    WHERE dhist.TRACCT = {acctno} AND dhist.TRDATE BETWEEN {start_date} AND {end_date}
                    UNION ALL
                    SELECT 
                            --AUXTRC,TRANCD,TRACCT,TRDATE,KREDIT,DEBIT,TRUSER,WAKTU,REMARK

                             AUXTRC,TRANCD,TRACCT,TRDATE
                            ,CASE WHEN DORC ='C' THEN amt ELSE 0 END AS KREDIT
                            ,CASE WHEN DORC ='D' THEN amt ELSE 0 END AS DEBIT
                            ,TRUSER
                            ,SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(TIMENT),7),' |,','0'),4,2) AS WAKTU
                            ,TRREMK
                            ,TRREMK AS REMARK 
                        FROM REKENING_KORAN.AS400_DDTRN2  
                            WHERE TRACCT  = {acctno} AND TRDATE = {end_date}
                    )
                    ORDER BY (TRDATE,WAKTU) ASC"""
        
        query3 = f"""SELECT dhist.AUXTRC as AUXTRC
                        ,dhist.TRANCD AS TRANCD
                        ,dhist.TRREMK AS TRREMK
                        ,dhist.TRACCT AS TRACCT
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
                        ,'' AS WAKTU
                        ,CASE
                        WHEN 
                        	TRREMK = '                                        ' AND TLBDS1 IS NULL AND TLBDS2 IS NULL   
                        	THEN RTRIM(DDPAR3."DESC") 
						WHEN RTRIM(TRREMK) = RTRIM(TLBDS1)  THEN  ARRAY_TO_STRING(ARRAY[TRREMK ,TLBDS2],' ')
						WHEN RTRIM(TRREMK) = RTRIM(TLBDS2)  THEN  ARRAY_TO_STRING(ARRAY[TRREMK ,TLBDS1],' ')
						ELSE ARRAY_TO_STRING(ARRAY[TRREMK,TLBDS1,TLBDS2],' ')
						END AS REMARK 
                FROM REKENING_KORAN.AS400_DDDHIS dhist
                INNER JOIN REKENING_KORAN.AS400_DDPAR3 DDPAR3
                ON dhist.TRANCD = DDPAR3.TRANCD
                WHERE dhist.TRACCT = {acctno} AND dhist.TRDATE BETWEEN {start_date} AND {end_date} 
                --and dhist.TRANCD = 198
                ORDER BY (dhist.TRDATE,dhist.TRTIME) ASC """


        if con == 1 :
            run = Config.run_query(self, query1)
            return run
        if con == 2 :
            run = Config.run_query(self, query2)
            return run
        if con == 3 or con == 4 :
            run = Config.run_query(self, query3)
            return run
        else : 
            return False
        
    #2. LOAN
    def loanDemografiQuery(self,acctno) :
        query = f"""
            SELECT 
                ARRAY_TO_STRING(ARRAY[GELAR_SEBELUM_NAMA ,NAMA_LENGKAP,GELAR_SESUDAH_NAMA],' ') AS NAMA,
                ARRAY_TO_STRING(ARRAY[ALAMAT_ID1,ALAMAT_ID2,ALAMAT_ID3],' ') AS ALAMAT,
                current_date() AS TANGGAL_LAPORAN,
                ACCTNO,
                RTRIM(e.JDNAME) AS UNIT_KERJA,ARRAY_TO_STRING(ARRAY[RTRIM(e.JDADDR) ,RTRIM(e.JDCSZ)],' ') AS ALAMAT_UNIT_KERJA,
                RTRIM(f.PTYDSC) AS PRODUCT,
                d.CURTYP AS VALUTA,
                PERKIRAAN_TAGIHAN_BULAN_INI,
                TUNGGAKAN
            FROM  CHUB_DEMOGRAPHY c 
            JOIN 
            (SELECT 
                a.CIFNO,a.ACCTNO,a.BR, a."TYPE",a.CURTYP,
                 (a.BILPRN + a.BILINT + a.BILESC + a.BILESC + a.BILLC + a.BILOC + a.BILMC ) AS PERKIRAAN_TAGIHAN_BULAN_INI,
            (a.BILPNO + a.BILINO + a.BILESO + a.BILLCO + a.BILOCO + a.BILMCO) AS TUNGGAKAN
            FROM REKENING_KORAN.AS400_LNMAST a
            WHERE a.ACCTNO ={acctno} )   AS d         
            ON c.CIFNO = d.CIFNO
            LEFT JOIN REKENING_KORAN.AS400_JHDATA e
            ON d.BR = e.JDBR
            LEFT JOIN REKENING_KORAN.AS400_LNPAR2 f
            ON RTRIM(d."TYPE") = RTRIM(f.PTYPE)""" 
        run = Config.run_query(self, query)
        return run

    def loanMutasiQuery(self,acctno,start_date,end_date,con) :
        start_date = Config.convertJulianDate(start_date)
        end_date = Config.convertJulianDate(end_date)
    
        query1 = f"""
            SELECT
                LTAXTC AS AUXTRC,
                SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),4,2) AS WAKTU,
                LTMACT AS TRACCT,
                LTMTRN AS TRANCD ,
                LTMREM AS TRREMK,
                LTMDAT as TRDATE,
                CASE WHEN
                    LTMDC = 'D' OR LTMTRN IN ('911','912','916','924','961','962','965','966') THEN LTMAMT ELSE 0 
                END AS DEBIT,
                CASE WHEN 
                    LTMDC = 'C' AND LTMTRN NOT IN ('911','912','916','924','961','962','965','966') THEN LTMAMT ELSE 0 
                END AS KREDIT
                FROM REKENING_KORAN.AS4_LNMTRN 
                WHERE LTMACT = {acctno}
                AND LTMDAT  between {start_date} and {end_date}"""

        query2 = f"""SELECT 
                        LTAXTC AS AUXTRC,
                        LTMDAT AS TRDATE,
                        TO_NUMBER(LTMTRN) AS TRANCD,
                        SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LTMTIM),7),' |,','0'),4,2) AS WAKTU,
                        LTMACT AS TRACCT,
                        LTMREM AS TRREMK ,
                        CASE WHEN
                            LTMDC = 'D' OR LTMTRN IN ('911','912','916','924','961','962','965','966') THEN LTMAMT ELSE 0 
                        END AS DEBIT,
                        CASE WHEN 
                            LTMDC = 'C' AND LTMTRN NOT IN ('911','912','916','924','961','962','965','966') THEN LTMAMT ELSE 0 
                        END AS KREDIT
                        FROM REKENING_KORAN.AS4_LNMTRN 
                        WHERE LTMACT = {acctno}
                        AND LTMDAT = {end_date}
                    UNION ALL                
                    SELECT 
                        LHAXTC AS AUXTRC,
                        LHPSTD AS TRDATE,
                        LHTRAN AS TRANCD,
                        SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),4,2) AS WAKTU,
                        LHACCT AS TRACCT,
                        LHREMK AS TRREMK,
                        CASE WHEN
                            LHDORC = 'D' OR LHTRAN IN (911,912,916,924,961,962,965,966) THEN LHAMT ELSE 0 
                        END AS DEBIT,
                        CASE WHEN 
                            LHDORC = 'C' AND LHTRAN NOT IN (911,912,916,924,961,962,965,966) THEN LHAMT ELSE 0 
                        END AS KREDIT
                    FROM REKENING_KORAN.AS4_LNDHIST 
                        WHERE LHACCT = {acctno}
                            AND LHPSTD  between {start_date} and {end_date}"""

        query3 = f"""SELECT 
                        LHAXTC AS AUXTRC,    
                        LHPSTD AS TRDATE,
                        SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),1,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),3,2)||':'||SUBSTR(REGEXP_REPLACE(LPAD(TO_CHAR(LHTIME),7),' |,','0'),4,2) AS WAKTU,
                        LHACCT AS TRACCT,
                        LHREMK AS TRREMK,
                        LHTRAN AS TRANCD,
                        CASE WHEN
                            LHDORC = 'D' OR LHTRAN IN (911,912,916,924,961,962,965,966) THEN LHAMT ELSE 0 
                        END AS DEBIT,
                        CASE WHEN 
                            LHDORC = 'C' AND LHTRAN NOT IN (911,912,916,924,961,962,965,966) THEN LHAMT ELSE 0 
                        END AS KREDIT
                    FROM REKENING_KORAN.AS4_LNDHIST 
                        WHERE LHACCT = {acctno} AND LHPSTD  between {start_date} and {end_date} order by LHPSTD asc"""

        if con == 1 :
            run = Config.run_query(self, query1)
            return run
        if con == 2 :
            run = Config.run_query(self, query2)
            return run
        if con == 3 or con == 4 :
            run = Config.run_query(self, query3)
            return run
        else : 
            return False

    #QUERY TESTING 
    def test_query(self, acctno, start_date, end_date,con) :
        return 'test'

    #Method to running Query
    def toDate(self,str) : 
        str =  datetime.datetime.strptime(str ,"%Y%m%d")
        yesterday = str - timedelta(1)
        yesterday = yesterday.strftime("%Y%m%d")
        return yesterday


    def run_query(self,sql) :
        Config._cursor = Config.__connection.cursor()
        Config._cursor.execute(sql)
        
        return Config._cursor       

    def convertJulianDate(date):
        date=datetime.datetime.strptime(date,'%Y%m%d')
        date=int(str(date)[:4]+str(date.strftime('%j')))
        return date