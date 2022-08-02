import time
from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None

    def __init__(self):
        Models._Singleton = Config()
    
    def get_all(self) :
        getRecords = Models._Singleton.All()


    def Mutasi(self,acctno, start_date, end_date) :
    
        # getRecord = Models._Singleton.eachRecord(acctno)
        getRecord = Models._Singleton.dummy_query(acctno)
        field_map = Models.fields(getRecord)

        mutasi = []
        for row in getRecord :
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','tanggalEfektif','jamTransaksi','kodeTransaksi','deskTran',
            'saldoAwal','mutasiKredit','mytasiDebit','saldoAkhr' ])

            temp['NoRek']	            =  row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    =row[field_map['TRDATE']]	
            temp['tanggalEfektif']	    =row[field_map['TRDATE']]	
            temp['jamTransaksi']	    =row[field_map['TRTIME']]	
            temp['kodeTransaksi']	    = row[field_map['TRNCD'] ]	
            temp['deskTran']	        =""	
            temp['saldoAwal']	        =""	
            temp['mutasiKredit']        =row[field_map['Kredit']]	
            temp['mytasiDebit']	        = row[field_map['Debit']]	
            temp['saldoAkhr']	        =""	

            mutasi.append(temp)
        return mutasi    
                     
    
#TO GET FIELD NAMES FROM TABLES
    def fields(conn) :
        results = {}
        column = 0

        for d in conn.description :
            results[d[0]] = column
            column = column + 1 
        return results
                