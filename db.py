# import phoenixdb
# import phoenixdb.cursor


import mysql.connector 
from mysql.connector import Error

class Config:

    _cursor = None
    __connection = None
    __instance__ = None 

    def __init__(self) :
            try :
                #Config.__connection =phoenixdb.connect('http://hbdcm01.hq.bri.co.id:8765/', autocommit=True, auth="SPNEGO")
                Config.__connection = mysql.connector.connect(host='localhost', user='root', password='P@ssw0rd', db='classicmodels') 
            except:
                print("Error while connect to Phoenix") 
    #SINGLETON PATTERN
    # @staticmethod
    # def getInstance():
    #     if not Config.__instance__:
    #         Config()
    #     return Config.__instance__

    #GEET DEMOGRAFI RECORD    
    def demografiQuery(self,acctno) :
        query =f"""
                SELECT 
                    GELAR_SEBELUM_NAMA ,NAMA_LENGKAP,GELAR_SESUDAH_NAMA,ACCTNO,
                    ALAMAT_ID1, ALAMAT_ID2,ALAMAT_ID3,ALAMAT_ID4,d.BRDESC AS UNIT_KERJA,
                    current_date() AS TanggalLaporan,jenis_pekerjaan    AS Pekerjaan,
                    ALAMAT_KANTOR4, RT_KANTOR, RW_KANTOR, KELURAHAN_KANTOR,KECAMATAN_KANTOR, KOTA_KANTOR, PROPINSI_KANTOR, KODEPOS_KANTOR,
                    PRODUCT,
                    CURRENCY
                    FROM  CHUB_DEMOGRAPHY c 
                    JOIN 
                        (SELECT 
                            a.CIFNO,a.ACCTNO,a.PRODUCT,a.CURRENCY,a.BRDESC
                        FROM CHUB_SAVING a
                        WHERE a.CIFNO IN 
                        (SELECT b.CIFNO FROM REKENING_KORAN.DDMAST b
                        WHERE  b.ACCTNO ='{acctno}')
                        AND a.ACCTNO like '%{acctno}' ) AS d
                    ON c.CIFNO = d.CIFNO"""	
        run = Config.run_query(self, query)
        return run


    def eachRecord(self, acctno, start_date, end_date) : 
        print(start_date)
        print(end_date)
        query = f"""
                 SELECT ACCTNO,CBAL,d.*  
                 FROM REKENING_KORAN.DDMAST ddmast
                    JOIN 
                    (SELECT 
                        dhist.TRANCD 	
                        ,dhist.TRACCT
                        ,dhist.TRDATE 
                        ,CASE 
                            WHEN dhist.TRDORC ='C' THEN dhist.amt
                            ELSE 0
                        END AS Kredit
                        ,CASE	
                            WHEN dhist.TRDORC ='D' THEN dhist.amt 
                            ELSE 0
                        END AS Debit
                        ,dhist.TRUSER 
                        ,dhist.TRREMK 
                        ,dhist.TRTIME
                        ,dhist.TLBDS1
                        ,dhist.TLBDS2	
                FROM REKENING_KORAN.DL_DDHIST dhist
                WHERE dhist.TRACCT = '{acctno}' AND TO_NUMBER(dhist.TRDATE) BETWEEN {start_date} AND {end_date}) AS d
                ON ddmast.ACCTNO = d.TRACCT
                ORDER BY (d.TRDATE,d.TRTIME) ASC""" 

        run = Config.run_query(self, query) 
        # for row in run :
        return run

    def dummy_query(self, acctno,start_date, end_date) :

        query = f""" 
            select 
                CBAL,
                 TRACCT 
                ,TRDATE
                ,CASE 
                    WHEN    TRDORC ='C' THEN amt
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