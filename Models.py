from datetime import datetime
import datetime

from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None

    #INSTANCE OBJECT THIS CLASS    
    def __init__(self):
        Models._Singleton = Config()
    
    def demografi(self,acctno,start_date,end_date):
        demografi = Models._Singleton.demografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi)

        start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")
           

        alamat_kantor= ""    
        for row in demografi :
            
            row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ]
            alamat_kantor= "%s %s" % (row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ])

            dict = {
                    'nama'                : row[field_map['NAMA_LENGKAP']]
                    ,'Alamat'              : row[field_map['ALAMAT_ID1']]
                    ,'nomorRekening'       : row[field_map['ACCTNO']]
                    ,'namaProduk'          : row[field_map['PRODUCT']]
                    ,'valuta'              : row[field_map['CURRENCY']]
                    ,'tanggalLaporan'      : row[field_map['TANGGALLAPORAN']].strftime("%d/%m/%d/%y")
                    ,'periodeTransaksi'    : start_date+"-"+end_date
                    ,'unitKerja'           : row[field_map['UNIT_KERJA']]
                    ,'alamatUnitKerja'     : alamat_kantor
            }
            
            return dict

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date) :

        #CONVERT JULIAN DATE
        start_date = Models.convertJulianDate(start_date)
        end_date = Models.convertJulianDate(end_date)
        
        #retrive acctno to lookup ddmast table 
        #getRecords = Models._Singleton.eachRecord(acctno, start_date, end_date) #get record from dl_ddhist
        

        getRecords = Models._Singleton.dummy_query(acctno,start_date,end_date)
        field_map = Models.fields(getRecords)
        
        #get CBAL from previous period    
        
        saldo_awal = 30000                    
        mutasi = []
        
        for row in getRecords :
            # saldo_awal = saldo_awal - debit + kredit
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','tanggalEfektif','jamTransaksi','kodeTransaksi','deskTran',
            'saldoAwal','mutasiKredit','mutasiDebit','saldoAkhir' ])

            
            kredit = row[field_map['Kredit']]        
            debit = row[field_map['Debit']]
            

            temp['NoRek']	            = row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    = row[field_map['TRDATE']]
            temp['tanggalEfektif']	    =row[field_map['TRDATE']]	
            temp['jamTransaksi']	    =row[field_map['TRTIME']]   
            temp['kodeTransaksi']	    = row[field_map['TRNCD'] ]	
            temp['deskTran']	        =""	
            temp['saldoAwal']	        = saldo_awal
            temp['mutasiKredit']        =row[field_map['Kredit']]	
            temp['mutasiDebit']	        = row[field_map['Debit']]	
            temp['saldoAkhir']	        =  transaksi = saldo_awal  - debit + kredit

            mutasi.append(temp)
            # saldo_awal = transaksi
        return mutasi    

    #FUNCTION TO SHOW
    # def outputView(self,body,demografi):
    def outputView(self, body):
        data = {'Response' : 
        {
        "statusCode": 200,
        "errorCode": "000",
        "responseCode": "00",
        "responseMessage": "Success",
        "errors": "null"
        ,"Data" :{
                    # "Header" : demografi,
                    "Body" : body
                 }
                    
                 #closing of Data
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
        date=datetime.datetime.strptime(date,'%Y%m%d')
        date=int(str(date)[:4]+str(date.strftime('%j')))
        return date

    
        
        
