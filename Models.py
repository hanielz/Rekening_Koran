from datetime import datetime
from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None

    #INSTANCE OBJECT THIS CLASS    
    def __init__(self):
        Models._Singleton = Config()
    
    def get_all(self) :
        getRecords = Models._Singleton.All()

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date) :
        julian = Models.convertJulianDate(self, start_date)
        print(julian)
        getRecord = Models._Singleton.eachRecord(acctno)
        # getRecord = Models._Singleton.dummy_query(acctno)
        field_map = Models.fields(getRecord)

        mutasi = []
        for row in getRecord :
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','tanggalEfektif','jamTransaksi','kodeTransaksi','deskTran',
            'saldoAwal','mutasiKredit','mytasiDebit','saldoAkhr' ])

            temp['NoRek']	            =  row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    =row[field_map['TRDATE']]	
            temp['tanggalEfektif']	    =row[field_map['TRDATE']]	
            temp['jamTransaksi']	    =row[field_map['TRTIME']]	
            temp['kodeTransaksi']	    = row[field_map['TRANCD'] ]	
            temp['deskTran']	        =""	
            temp['saldoAwal']	        =""	
            temp['mutasiKredit']        =row[field_map['KREDIT']]	
            temp['mytasiDebit']	        = row[field_map['DEBIT']]	
            temp['saldoAkhr']	        =""	

            mutasi.append(temp)
        return mutasi    

    def outputView(self, keyValue):
        data = {'Response' : 
        {
        "statusCode": 200,
        "errorCode": "000",
        "responseCode": "00",
        "responseMessage": "Success",
        "errors": "null"
        ,"Data" : 
                {
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
                    ,"Body" :keyValue
                } #closing of Data
        }  #closing of response     
        } #closing of data       

        return data

## OTHER FUNCTION REQUIRED ##
    #1. TO GET FIELD NAMES FROM TABLES :
    def fields(conn) :
        results = {}
        column = 0

        for d in conn.description :
            results[d[0]] = column
            column = column + 1 
        return results
    
    #2.Convert to Julian Date :
    def convertJulianDate(self, date):
        date=datetime.strptime(date,'%Y%m%d')
        date=int(str(date)[:4]+str(date.strftime('%j')))
        return date
