import phoenixdb
import phoenixdb.cursor


# import mysql.connector 
# from mysql.connector import Error

class Config:

    _cursor = None
    __connection = None
    __instance__ = None 

    def __init__(self) :
            try :
                Config.__connection =phoenixdb.connect('http://hbdcm01.hq.bri.co.id:8765/', autocommit=True, auth="SPNEGO")
                #Config.__connection = mysql.connector.connect(host='localhost', user='root', password='P@ssw0rd', db='classicmodels') 
            except:
                print("Error while connect to Phoenix") 
    #SINGLETON PATTERN
    # @staticmethod
    # def getInstance():
    #     if not Config.__instance__:
    #         Config()
    #     return Config.__instance__

    def All(self) :
        run = Config.run_query(self, "SELECT ACCTNO,CIFNO,TRANSACTIONID FROM REKENING_KORAN.DDMAST  LIMIT 5")
        return run

    def eachRecord(self, acctno) : 
        query = f"""SELECT 
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
                        ,dhist.TRANCD
                        ,dhist.TLBDS1
                        ,dhist.TLBDS2	
                        FROM REKENING_KORAN.DL_DDHIST dhist
                    where TRACCT='{acctno}'"""

        run = Config.run_query(self, query)
        # for row in run :
        return run

    def dummy_query(self, acctno) :
        query = f"""
            select
                dhist.TRNCD    
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
                ,dhist.TLBDT1
                ,dhist.TLBDS2
                from DL_DHIST dhist
                where dhist.TRACCT= {acctno};
                     """
        run = Config.run_query(self, query)
        
        return run

    #Method to running Query
    def run_query(self,sql) :
        Config._cursor = Config.__connection.cursor()
        Config._cursor.execute(sql)
        
        return Config._cursor