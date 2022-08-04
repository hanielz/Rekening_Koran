from datetime import datetime
from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None

    #INSTANCE OBJECT THIS CLASS    
    def __init__(self):
        Models._Singleton = Config()
    
    def demografi(self,acctno):
        demografi = Models._Singleton.demografiQuery(acctno)
        field_map = Models.fields(demografi)

        demo = []
        full= ""    
        for row in demografi :
            
            # row[field_map['GELAR_SEBELUM_NAMA']],row[field_map['NAMA_LENGKAP']],row[field_map['GELAR_SESUDAH_NAMA']]
            # full = "%s %s %s" % ("DR" ,row[field_map['NAMA_LENGKAP']], "S.T")
            dict = {
                    'nama'                : row[field_map['NAMA_LENGKAP']]
                    ,'Alamat'              : row[field_map['ALAMAT_ID1']]
                    ,'nomorRekening'       : row[field_map['ACCTNO']]
                    ,'namaProduk'          : row[field_map['PRODUCT']]
                    ,'valuta'              : row[field_map['CURRENCY']]
                    ,'tanggalLaporan'      : row[field_map['TANGGALLAPORAN']]    
                    ,'periodeTransaksi'    : ""
                    ,'pekerjaan'           : row[field_map['PEKERJAAN']]
                    ,'alamatKantor'        : row[field_map['ALAMAT_KANTOR3']]
            }
            
            return dict

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date) :

        #CONVERT JULIAN DATE
        start_date = Models.convertJulianDate(start_date)
        end_date = Models.convertJulianDate(end_date)
        
         #retrive acctno to lookup ddmast table 
        getRecord = Models._Singleton.eachRecord(acctno, start_date, end_date) #get record from dl_ddhist
        # getRecord = Models._Singleton.dummy_query(acctno)
        field_map = Models.fields(getRecord)

        mutasi = []

        for row in getRecord :
            saldo_awal = row[field_map['CBAL']]	
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','tanggalEfektif','jamTransaksi','kodeTransaksi','deskTran',
            'saldoAwal','mutasiKredit','mytasiDebit','saldoAkhr' ])

            temp['NoRek']	            =  row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    =row[field_map['TRDATE']]	
            temp['tanggalEfektif']	    =row[field_map['TRDATE']]	
            temp['jamTransaksi']	    =row[field_map['TRTIME']]	
            temp['kodeTransaksi']	    = row[field_map['TRANCD'] ]	
            temp['deskTran']	        =""	
            temp['saldoAwal']	        = float(saldo_awal)
            temp['mutasiKredit']        =row[field_map['KREDIT']]	
            temp['mytasiDebit']	        = row[field_map['DEBIT']]	
            temp['saldoAkhr']	        = ""

            saldo_awal= saldo_awal - row[field_map['KREDIT'] ] + row[field_map['DEBIT'] ]
            mutasi.append(temp)
        return mutasi    

    def outputView(self, body,demografi):
        data = {'Response' : 
        {
        "statusCode": 200,
        "errorCode": "000",
        "responseCode": "00",
        "responseMessage": "Success",
        "errors": "null"
        ,"Data" : 
                {
                    "Header":demografi

                    ,"Body" :body
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
    def convertJulianDate(date):
        date=datetime.strptime(date,'%Y%m%d')
        date=int(str(date)[:4]+str(date.strftime('%j')))
        return date
