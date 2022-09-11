from Procedure import Procedure
import decimal
import datetime


class Models(Procedure) :
    
    #_Singleton = None
    # footer = ""
    # saldo_awal=0
    # transaksi=0
    # acctno=""
    # start_date=""
    # end_date=""

    #INSTANCE OBJECT THIS CLASS    
    # def __init__(self):
    #     Procedure._Singleton = Config()
    
    def demografi(self,acctno,start_date,end_date):
        demografi = Procedure._Singleton.demografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi)

        start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")
           
        for row in demografi :
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

    def loanDemografi(self,acctno,start_date,end_date) :
        demografi_loan = Procedure._Singleton.loanDemografiQuery(acctno) #retrive date from Database
        field_map = Models.fields(demografi_loan)

        # start_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%d/%m/%y")
        # end_date =  datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")

        for row in demografi_loan :
            dict = {
                        'nama'                  : row[field_map['NAMA']]
                        ,'nomorRekening'        : row[field_map['ACCTNO']] 
                        ,'alamat'               : row[field_map['ALAMAT']] 
                        ,'namaProduk'           : row[field_map['PRODUCT']]
                        ,'valuta'               : row[field_map['VALUTA']] 
                        ,'tanggalLaporan'       : row[field_map['TANGGAL_LAPORAN']]
                        # ,'periodeTransaksi'    : start_date+"-"+end_date
                        ,'alamatUnitKerja'      : row[field_map['ALAMAT_UNIT_KERJA']]
                        ,'perkiraanTagihanBulanIni' : row[field_map['PERKIRAAN_TAGIHAN_BULAN_INI']]
                        ,'tunggakan' : row[field_map['TUNGGAKAN']]
                }
            return dict


    #FUNCTION TO GET TRANSACTION FROM DL_DDHIST
    def Mutasi(self,acctno, start_date, end_date,type) :
                    
        #1. GET CASA TRANSACTION
        getLogicMutasi = Procedure.getLogicMutasi(self,acctno,start_date,end_date,type)
        field_map = Procedure.fields(getLogicMutasi)

        #2. AMBIL SALDO AWAL
        get_saldo=Procedure.getsaldo(self, acctno,start_date,type)
        Procedure.debit  =   Procedure.sumDebitKredit('DEBIT',type)
        Procedure.kredit = Procedure.sumDebitKredit('KREDIT',type)
        
        saldo_awal = get_saldo + Procedure.sumDebitKredit('DEBIT',type) - Procedure.sumDebitKredit('KREDIT',type)
        Procedure.saldo_awal = saldo_awal    #assign to class variable 
        

        print( "cbal  : ", get_saldo )
        print("Debit : " ,Procedure.sumDebitKredit('DEBIT',type))
        print("Kredit : " , Procedure.sumDebitKredit('KREDIT',type))
        print( "saldo awal : ", Procedure.saldo_awal, "\n" )
        

        mutasi_rekening = []
        for row in getLogicMutasi :
            temp = dict.fromkeys(['NoRek','tanggalTransaksi','jamTransaksi','teller','uraianTransaksi',
            'saldoAwal','mutasiKredit','mutasiDebit','saldoAkhir' ])

            temp['NoRek']	            = row[field_map['TRACCT']]	
            temp['tanggalTransaksi']    = Procedure.convertJuliandateTostandart(row[field_map['TRDATE']])
            temp['jamTransaksi']	    = row[field_map['WAKTU']]   

            if type == 'casa' :
                temp['teller']	            = row[field_map['TRUSER']]
                
            #trremk_string =  len(row[field_map['TRREMK']].strip())
            if row[field_map['TRREMK']] is None :
                get_remark = Procedure.getremark(self,start_date ,end_date, row[field_map['AUXTRC']], row[field_map['TRANCD']] ,row[field_map['TRREMK']],row[field_map['TRREMK']])
                temp['uraianTransaksi']	    = get_remark
                print(get_remark)
            else :
                if type == 'casa' :
                    temp['uraianTransaksi']	    = row[field_map['REMARK'] ]
            temp['saldoAwal']	        = "{:0,.2f}".format(saldo_awal)
            temp['mutasiKredit']        =  "{:0,.2f}".format(row[field_map['KREDIT']])	
            temp['mutasiDebit']	        =  "{:0,.2f}".format(row[field_map['DEBIT']]) 

            Procedure.transaksi = saldo_awal - row[field_map['DEBIT']] + row[field_map['KREDIT']]

            temp['saldoAkhir']	        ="{:0,.2f}".format(Procedure.transaksi)
                
            saldo_awal = Procedure.transaksi
            mutasi_rekening.append(temp)
            
        return mutasi_rekening

    
    def Footer(self) : 
        footer = {
                "saldoAwalMutasi" :  "{:0,.2f}".format(Procedure.saldo_awal)
                ,"saldoAkhirMutasi" : "{:0,.2f}".format(Procedure.transaksi),
                "totalMutasiDebit" : "{:0,.2f}".format(Procedure.debit)
                ,"totalMutasiKredit": "{:0,.2f}".format(Procedure.kredit)
                ,"terbilang " : Procedure.ConvertTerbilang(Procedure.transaksi) + " Rupiah"
                }
        return footer




    #FUNCTION TO SHOW
    def outputView(self,body,demografi,Footer):
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
            
             ,"Footer" : Footer

                 #closing of Data
            }  #closing of response     
        } #closing of data       

        return data

## OTHER FUNCTION REQUIRED ##
    
    