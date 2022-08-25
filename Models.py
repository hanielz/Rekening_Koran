from Procedure import Procedure

from datetime import datetime
import datetime
import decimal

#from var_dump import var_dump

#from db import Config

class Models(Procedure) :
    
    #_Singleton = None
    footer = ""
    saldo_awal=0
    transaksi=0
    acctno=""
    start_date=""
    end_date=""

    #INSTANCE OBJECT THIS CLASS    
    # def __init__(self):
    #     Procedure._Singleton = Config()
    
    def demografi(self,acctno,start_date,end_date):
        demografi = Procedure._Singleton.demografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi)

        start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")
           
        for row in demografi :
            
            # row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ]
            # alamat_kantor= "%s %s" % (row[field_map['ALAMAT_KANTOR4']],row[field_map['KODEPOS_KANTOR'] ])
            
            dict = {
                    'nama'                : row[field_map['NAMA']]
                    ,'Alamat'              : row[field_map['ALAMAT']]
                    ,'nomorRekening'       : row[field_map['ACCTNO']]
                    ,'namaProduk'          : row[field_map['PRODUCT']]
                    ,'valuta'              : row[field_map['VALUTA']]
                    ,'tanggalLaporan'      : row[field_map['TANGGALLAPORAN']].strftime("%d/%m/%y")
                    ,'periodeTransaksi'    : start_date+"-"+end_date
                    ,'unitKerja'           : row[field_map['UNIT_KERJA']]
                    ,'alamatUnitKerja'     : row[field_map['ALAMAT_UNIT_KERJA']]
            }

            return dict

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def getsaldo(acctno):
        test=Procedure._Singleton.cbalQuery(acctno)
        for row in test :
            get_saldo = row[0]
            return get_saldo

    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date) :
        
        #ASSIGN CLASS VARIBALE to Local variable
        Models.acctno = acctno
        Models.start_date=start_date
        Models.end_date=end_date

        #CONVERT JULIAN DATE
        Models.start_date = Models.convertJulianDate(start_date)
        Models.end_date = Models.convertJulianDate(end_date)

        #tesProcedureRemark(self,'this is remark method')
        
        #gte cbal from ddmast
        get_saldo=Models.getsaldo(acctno) 

        #get record from dl_ddhist
        Mutasi = Procedure._Singleton.MutasiQuery(Models.acctno, Models.start_date, Models.end_date) 
        
        # Mutasi = Procedure._Singleton.dummy_query(Models.acctno, Models.start_date, Models.end_date)
        field_map = Models.fields(Mutasi)
                
        #get CBAL from previous period    
        saldo_awal = get_saldo + Models.FooterParameter('DEBIT') - Models.FooterParameter('KREDIT')
        
        Models.saldo_awal = saldo_awal                    
        mutasi_rekening = []
        
        for row in Mutasi :
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','jamTransaksi','teller','uraianTransaksi',
            'saldoAwal','mutasiKredit','mutasiDebit','saldoAkhir' ])

            get_remark =  Procedure.getremark(self,row[field_map['AUXTRC']], row[field_map['TRANCD']] ,row[field_map['TRREMK']],row[field_map['TRREMK']])
                

            temp['NoRek']	            = row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    = Models.convertJuliandateTostandart(row[field_map['TRDATE']])
            temp['jamTransaksi']	    = row[field_map['WAKTU']]   
            temp['teller']	            = row[field_map['TRUSER']]

            trremk_string =  len(row[field_map['TRREMK']].strip())
            if trremk_string == 0 :
                temp['uraianTransaksi']	    = "kosong", get_remark
                print("result get remark :" ,get_remark)
            else :
                temp['uraianTransaksi']	    = row[field_map['REMARK'] ]
            temp['saldoAwal']	        = "{:0,.2f}".format(saldo_awal)
            temp['mutasiKredit']        =  "{:0,.2f}".format(row[field_map['KREDIT']])	
            temp['mutasiDebit']	        =  "{:0,.2f}".format(row[field_map['DEBIT']]) 

            Models.transaksi = saldo_awal - row[field_map['DEBIT']]  + row[field_map['KREDIT']]

            temp['saldoAkhir']	        = "{:0,.2f}".format(Models.transaksi)
                
            saldo_awal = Models.transaksi
            
            mutasi_rekening.append(temp)
            
        return mutasi_rekening

    def testing(self,acctno) :
        # #CALL FUNCTIOPN FORM PROCEDURE CLASS
        get_remark = Procedure.getremark(self)

        return get_remark

    def FooterParameter(type) :
        Mutasi = Procedure._Singleton.MutasiQuery(Models.acctno, Models.start_date, Models.end_date)
        field_map = Models.fields(Mutasi)
        hitung=sum(row[field_map[type]] for row in Mutasi)
        # Models.total_debit=sum(row[field_map['Debit']] for row in Mutasi)
        return hitung ;

    ### LOAN METHOD ###
    def loanDemografi(self,acctno,start_date,end_date) :
        print(start_date,' ', end_date)
        demografi_loan = Procedure._Singleton.loanDemografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi_loan)
        # start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        # end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")

        for row in demografi_loan :
            dict = {
                        'nama'                 : row[field_map['SNAME']]
                        ,'nomorRekening'        : row[field_map['ACCTNO']] 
                        ,'perkiraanTagihan'     : row[field_map['PERKIRAAN_TAGIHAN_BULAN_INI']]
                        ,'periodeTransaksi'     : row[field_map['TUNGGAKAN']]
                }
            return dict


    def loanMutasi(self,acctno, start_date, end_date) : 
            mutasi_rekening = [] 
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','jamTransaksi','teller','uraianTransaksi',
            'saldoAwal','mutasiKredit','mutasiDebit','saldoAkhir' ])

            temp['NoRek']	            = acctno
            temp['tanggalTransaksi']    = start_date
            temp['jamTransaksi']	    = "12:00"
            temp['teller']	            = row[field_map['TRUSER']]
            temp['uraianTransaksi']	    = row[field_map['REMARK'] ]
            temp['saldoAwal']	        = 20,000,000
            temp['mutasiKredit']        =  350,132
            temp['mutasiDebit']	        =  0,0
            temp['saldoAkhir']	        = "{:0,.2f}".format(Models.transaksi)
            
            mutasi_rekening.append(temp)
            
            return mutasi_rekening

    #FUNCTION TO SHOW
    def outputView(self,body,demografi):
        data = {'Response' : 
        {
            "statusCode": 200,
            "errorCode": "000",
            "responseCode": "00",
            "responseMessage": "Success",
            "errors": "null"
            ,"Data" :{
                        "Header" : demografi,
                        "Body" : body
                    }
            #  ,"Footer" : {
            #               "saldoAwalMutasi" :  50000.00
            #              ,"saldoAkhirMutasi" : 6720.00
            #              ,"totalMutasiDebit" : 0
            #              ,"totalMutasiKredit": 210.00
            #              ,"terbilang " : "tiga ribu dua ratus rupiah"
            #             } 

            ,"Footer" : {
                          "saldoAwalMutasi" :  "{:0,.2f}".format(Models.saldo_awal)
                         ,"saldoAkhirMutasi" : "{:0,.2f}".format(Models.transaksi)
                         ,"totalMutasiDebit" : "{:0,.2f}".format(Models.FooterParameter('DEBIT'))
                         ,"totalMutasiKredit": "{:0,.2f}".format(Models.FooterParameter('KREDIT'))
                         ,"terbilang " : Models.ConvertTerbilang(Models.transaksi) + " Rupiah"
                        #  , "tes" : decimal.Decimal(Models.FooterParameter('DEBIT'))
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

    #Convert to Gergorian Date :
    def convertJuliandateTostandart(t):
        t = str(t)
        date=datetime.datetime.strptime(t, '%Y%j').date()
        result=date.strftime("%d/%m/%Y")
        return result
    
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
        
        
