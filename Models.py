import time
from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None

    def __init__(self):
        Models._Singleton = Config()
    
    def get_all(self) :
        getRecords = Models._Singleton.All()


    def get_record(self,acctno, start_date, end_date) :
        #hellow
        # start_date = time.strptime(start_date, '%Y-%m-%d')
        # getRecord = Models._Singleton.eachRecord(acctno)
        getRecord = Models._Singleton.dummy_query(acctno)
        field_map = Models.fields(getRecord)
        for row in getRecord :
            dict ={

                        'Response' : 
                    {
                        "statusCode": 200,
                        "errorCode": "000",
                        "responseCode": "00",
                        "responseMessage": "Success",
                        "errors": "null"
                        ,"Data" : {
                            "Header": 
                            {
                                "Nama": "Haniel Zefanya",
                                "Alamat": "null",
                                "NomorRekening": "null",
                                "NamaProduk": "null",
                                "Valuta": "null",
                                "TanggalLaporan": "null",					
                                "PeriodeTransaksi": "null",
                                "UnitKerja": "null",
                                "AlamatUnitKerja": "null"
                            }
                        ,"Body" :
                            { 
                                'NoRek'              : row[field_map['TRACCT']] 
                                ,'tanggalTransaksi'  : row[field_map['TRDATE']] 
                                ,'tanggalEfektif'    :  row[field_map['TRDATE']] 
                                ,'jamTransaksi' 	 :  row[field_map['TRTIME'] ] 
                                ,'kodeTransaksi' 	 :  row[field_map['TRANCD'] ]
                                ,'deskTran'  	     : ''
                                ,'saldoAwal'         :''
                                ,'mutasiKredit'      : row[field_map['KREDIT']] 
                                ,'mytasiDebit'       : row[field_map['DEBIT']] 
                                ,'saldoAkhr'         :''
                            }    
                        } #closing of Data
                        
                    } #closing of Response 

                } #closing of data variable
        return dict          
            
#TO GET FIELD NAMES FROM TABLES
    def fields(conn) :
        results = {}
        column = 0

        for d in conn.description :
            results[d[0]] = column
            column = column + 1 
        return results
                