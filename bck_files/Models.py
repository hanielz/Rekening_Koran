from datetime import datetime
import datetime

from var_dump import var_dump

from db import Config

class Models() :
    
    _Singleton = None
    footer = ""
    
    saldo_awal=0
    transaksi=0
    acctno=""
    start_date=""
    end_date=""

    #INSTANCE OBJECT THIS CLASS    
    def __init__(self):
        Models._Singleton = Config()
    
    def demografi(self,acctno,start_date,end_date):
        demografi = Models._Singleton.demografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi)

        start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")
           
        for row in demografi :
            
            # row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ]
            # alamat_kantor= "%s %s" % (row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ])

            dict = {
                    'nama'                : row[field_map['NAMA_LENGKAP']]
                    ,'Alamat'              : row[field_map['ALAMAT_ID1']]
                    ,'nomorRekening'       : row[field_map['ACCTNO']]
                    ,'namaProduk'          : row[field_map['PRODUCT']]
                    ,'valuta'              : row[field_map['CURRENCY']]
                    ,'tanggalLaporan'      : row[field_map['TANGGALLAPORAN']].strftime("%d/%m/%y")
                    ,'periodeTransaksi'    : start_date+"-"+end_date
                    ,'unitKerja'           : row[field_map['UNIT_KERJA']]
                    ,'alamatUnitKerja'     : row[field_map['ALAMATUNITKERJA']]
            }
            
            return dict

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date) :
        Models.acctno = acctno
        Models.start_date=start_date
        Models.end_date

        #CONVERT JULIAN DATE
        Models.start_date = Models.convertJulianDate(start_date)
        Models.end_date = Models.convertJulianDate(end_date)
    
        Mutasi = Models._Singleton.dummy_query(Models.acctno, Models.start_date, Models.end_date)
        field_map = Models.fields(Mutasi)

    
        #get CBAL from previous period    
        saldo_awal = 30000
        Models.saldo_awal = saldo_awal                    
        mutasi_rekening = []
        
        for row in Mutasi :
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','jamTransaksi','kodeTransaksi','deskTran',
            'saldoAwal','mutasiKredit','mutasiDebit','saldoAkhir' ])

    
            temp['NoRek']	            = row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    = row[field_map['TRDATE']]
            temp['jamTransaksi']	    =row[field_map['TRTIME']]   
            temp['kodeTransaksi']	    = row[field_map['TRNCD'] ]	
            temp['deskTran']	        =""	
            temp['saldoAwal']	        = saldo_awal
            temp['mutasiKredit']        =row[field_map['Kredit']]
            temp['mutasiDebit']	        = row[field_map['Debit']]	
            temp['saldoAkhir']	        = Models.transaksi = saldo_awal - row[field_map['Debit']]  + row[field_map['Kredit']]

            saldo_awal = Models.transaksi
            
            mutasi_rekening.append(temp)
            
            
            Models.footer = Models.ConvertTerbilang(Models.transaksi)
        return mutasi_rekening

   
    def FooterParameter(type) :
        Mutasi = Models._Singleton.dummy_query(Models.acctno, Models.start_date, Models.end_date)
        field_map = Models.fields(Mutasi)
        hitung=sum(row[field_map[type]] for row in Mutasi)
        # Models.total_debit=sum(row[field_map['Debit']] for row in Mutasi)
        return hitung ;

    #FUNCTION TO SHOW
    #def outputView(self,body,demografi):
    def outputView(self, body):
        data = {'Response' : 
        {
            "statusCode": 200,
            "errorCode": "000",
            "responseCode": "00",
            "responseMessage": "Success",
            "errors": "null"
            ,"Data" :{
                        #"Header" : demografi,
                        "Body" : body
                    }
            ,"Footer" : {
                          "saldoAwal" :  Models.saldo_awal
                         ,"saldoAkhir" : Models.transaksi
                         ,"totalMutasiDebit" : Models.FooterParameter('Debit')
                         ,"totalMutasiKredit": Models.FooterParameter('Kredit')
                         ,"terbilang " : Models.footer
                        #  ,"Saldo Akhir" :    
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

    #3.Terbilang :
    def ConvertTerbilang(bil):
        angka = ["","Satu","Dua","Tiga","Empat","Lima","Enam",
                "Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
        Hasil = " "
        n = int(bil)
        if n>= 0 and n <= 11:
            Hasil = angka[n]
        elif n <20:
            Hasil = Models.ConvertTerbilang (n-10) + " Belas "
        elif n <100:
            Hasil = Models.ConvertTerbilang (n/10) + " Puluh " + Models.ConvertTerbilang (n%10)
        elif n <200:
            Hasil = " Seratus " + Models.ConvertTerbilang (n-100)
        elif n <1000:
            Hasil = Models.ConvertTerbilang (n/100) + " Ratus " + Models.ConvertTerbilang (n%100)
        elif n <2000:
            Hasil = " Seribu " + Models.ConvertTerbilang (n-1000)
        elif n <1000000:
            Hasil = Models.ConvertTerbilang (n/1000) + " Ribu " + Models.ConvertTerbilang (n%1000)
        elif n <1000000000:
            Hasil = Models.ConvertTerbilang (n/1000000) + " Juta " + Models.ConvertTerbilang (n%1000000)
        elif n <1000000000000:
            Hasil = Models.ConvertTerbilang (n/1000000000) + " Milyar " + Models.ConvertTerbilang (n%1000000000)
        elif n <1000000000000000:
            Hasil = Models.ConvertTerbilang (n/1000000000000) + " Triliyun " + Models.ConvertTerbilang (n%1000000000000)
        elif n == 1000000000000000:
            Hasil = "Satu Kuadriliun"
        else:
            Hasil = "Angka Hanya Sampai Satu Kuadriliun"

        return Hasil
        
        
