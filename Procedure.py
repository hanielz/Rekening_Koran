import datetime
from datetime import datetime,date
from db import Config

class Procedure(object) : 

    _Singleton = None
    desk_tran = ''
    con = 0
    debit = 0 
    kredit = 0 

    footer = ""
    saldo_awal=0
    transaksi=0
    acctno=""
    start_date=""
    end_date=""

    #constructor contain connection 
    def __init__(self):
        try : 
            Procedure._Singleton = Config()
        except :
            print("Error when create Config Object !")

    def getremark(self,start_date ,end_date ,auxtrc, trancd,eftacc, trremk) : 
        #auxtrc,trancd ,eftacc, trremk
    
        #variable local 
        desk_tran = ''
        tlxaft = ''

        print("auxtrc :", auxtrc)
        print("trancd :",trancd)
        print("eftacc :" ,eftacc)
        print("trremk :", trremk)

        #GET TRANCD, TLXDS, TLXAFT
        getTrancd = Procedure._Singleton.trancdQuery(trancd) #get TRANCD form DDPAR3
        

        print("GET TRANCD form DDPAR3 : ", getTrancd)
        
        #JIKA AUXTRC <> NULL
        if (auxtrc is not None  ):  
            getTltxds = Procedure._Singleton.tltxdsQuery(auxtrc)  #Gget tltxds from AS400_TLTX
            getTltxaft = Procedure._Singleton.tltxaftQuery(auxtrc)  #Gget tltxaft from AS400_TLTX
            print("GET tltxds from AS400_TLTX : ", getTltxds)
            print("GET tltxaft from AS400_TLTX : ",getTltxaft)

            lxaft= getTltxaft  
            #RANGE to STRING
            # Procedure.rangeString(self,auxtrc )
            if (tlxaft =='A1' or auxtrc in('0688','0689') and Procedure.rangeString(self,auxtrc,716,712 ) == True):
                desk_tran = getTltxds
                if trancd == getTrancd :
                    desk_tran = trremk
                else :                              
                    desk_tran = getTltxds

                if auxtrc in ('8518','8506') :
                    desk_tran = 'TRANSFER ' + desk_tran

            if tlxaft =='A1' :
                if (trremk !='') : 
                    desk_tran=trremk
                else :    
                    desk_tran=getTltxds	
        
        #JIKA AUXTRC == NULL            
        if auxtrc is None : 
            if trremk is not None : 
                desk_tran = trremk
            else :
                desk_tran = Procedure._Singleton.descDdpar3Query(trancd)
            if trancd == '155' :
                desk_tran = 'BUNGA DEPOSITO ' + desk_tran
            
            return desk_tran

    def getLogicMutasi(self, acctno,start_date,end_date,type):

        print("tipe trnasaksi : ", type)
        Procedure.acctno = acctno
        Procedure.start_date = start_date
        Procedure.end_date = end_date

        #TANGGAL,BULAN,TAHUN  YG SAMA
        if (start_date == Procedure.getToday(self)) and (end_date == Procedure.getToday(self)) : 
            con = 1 
            Procedure.con = con
            print('tnaggal awal == hari ini dan tanggal akhir == hari ini  ')
            if type == 'casa' :
                return Procedure._Singleton.casaMutasiQuery(acctno,start_date,end_date,con)
            if type == 'loan' :
                return Procedure._Singleton.loanMutasiQuery(acctno,start_date,end_date)

        #BULAN DAN TAHUN YG SAMA, di mana tgl_awal < hari ini && tgl_akhir == hari ini
        if (start_date[6:8] < Procedure.getToday(self)[6:8] )and (end_date[6:8] == Procedure.getToday(self)[6:8]): 
            con = 2
            Procedure.con = con
            print('tanggal awal < hari ini & tanggal akhir = hari ini tapi dibulan ini')

            if type == 'casa' :
                return Procedure._Singleton.casaMutasiQuery(acctno,start_date,end_date,con)
            if type == 'loan' :
                return Procedure._Singleton.loanMutasiQuery(acctno,start_date,end_date,con)

        #BULAN DAN TAHUN YG SAMA, di mana tgl_awal < hari ini && tgl_akhir < hari ini
        if start_date[6:8] < Procedure.getToday(self)[6:8] and  end_date[6:8] < Procedure.getToday(self)[6:8] :
            con = 3
            Procedure.con = con
            print('tanggal awal < hari ini dan tanggl akhir < hari  ini  tapi dibulan ini')
            
            if type == 'casa' :
                return Procedure._Singleton.casaMutasiQuery(acctno,start_date,end_date,con)
            if type == 'loan' :
                return Procedure._Singleton.loanMutasiQuery(acctno,start_date,end_date,con)

        #TANGGAL,BULAN, TAHUN YG BEDA
        if start_date[0:8] < Procedure.getToday(self)[0:8] :
            con = 4
            Procedure.con = con
            print("tanggal awal < hari ini dan tanggal awal < bulan ini ") 

            if type == 'casa' :
                return Procedure._Singleton.casaMutasiQuery(acctno,start_date,end_date,con)
            if type == 'loan' :
                return Procedure._Singleton.loanMutasiQuery(acctno,start_date,end_date,con)
            

    def getsaldo(self, acctno,start_date, type):
        print("getSaldo:tipe trx : ", type)
        if (Procedure.con == 4) :
            #start_date[0:6] < Procedure.getToday(self)[0:6] : 
            conCbal = 1 
            if type == 'casa' :
                getCbal = Procedure._Singleton.cbalQuery(acctno,start_date,conCbal)
            if type == 'loan' :
                getCbal = Procedure._Singleton.cbalQueryLoan(acctno,start_date) 

            for row in getCbal :
                return row[0]

        if (Procedure.con == 1 or Procedure.con == 2 or Procedure.con == 3) :  
            conCbal = 2
            
            if type == 'casa' :
                getCbal = Procedure._Singleton.cbalQuery(acctno,start_date,conCbal)
            if type == 'loan' :
                getCbal = Procedure._Singleton.cbalQueryLoan(acctno,start_date) 

            for row in getCbal :
                return row[0]
        else : 
            return False


    def getsaldoloan(acctno,start_date):
        test=Procedure._Singleton.cbalQueryLoan(acctno,start_date)
        for row in test :
            return  row[0]

    #TO CREATE FOOTER untuk hitung debit dan kredit    
    def sumDebitKredit(type,typetrx) :
        print("Procedure.con : " ,Procedure.con)
    
    
        if typetrx == 'casa' :
            Mutasi = Procedure._Singleton.casaMutasiQuery(Procedure.acctno, Procedure.start_date, Procedure.end_date,Procedure.con)
            field_map = Procedure.fields(Mutasi)
            hitung=sum(row[field_map[type]] for row in Mutasi)
            return hitung
        if typetrx == 'loan' :
            Mutasi =  Procedure._Singleton.loanMutasiQuery(Procedure.acctno, Procedure.start_date, Procedure.end_date,Procedure.con)
            field_map = Procedure.fields(Mutasi)
            hitung=sum(row[field_map[type]] for row in Mutasi)
            return hitung
        

       
            
    def rangeString(self,x,startRange, endRange) :
        for i in range(startRange, endRange):
            convertToString=str(i).zfill(4)
            print(convertToString, 'auxtrc : ', x)
            if convertToString == x :return True 
            else : return False
    
    #get today :
    def getToday(self) : 
        date = datetime.today()
        result=date.strftime("%Y%m%d")
        return result

    def fields(conn) :
        results = {}
        column = 0
        
        for d in conn.description :
            results[d[0]] = column
            column = column + 1 
        return results
        
    #Convert to Gergorian Date :
    def convertJuliandateTostandart(t):
        t = str(t)
        date=datetime.strptime(t, '%Y%j').date()
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
            Hasil = Procedure.ConvertTerbilang (n-10) + " Belas "
        elif n <100:
            Hasil = Procedure.ConvertTerbilang (n/10) + " Puluh " + Procedure.ConvertTerbilang (n%10)
        elif n <200:
            Hasil = " Seratus " + Procedure.ConvertTerbilang (n-100)
        elif n <1000:
            Hasil = Procedure.ConvertTerbilang (n/100) + " Ratus " + Procedure.ConvertTerbilang (n%100)
        elif n <2000:
            Hasil = " Seribu " + Procedure.ConvertTerbilang (n-1000)
        elif n <1000000:
            Hasil = Procedure.ConvertTerbilang (n/1000) + " Ribu " + Procedure.ConvertTerbilang (n%1000)
        elif n <1000000000:
            Hasil = Procedure.ConvertTerbilang (n/1000000) + " Juta " + Procedure.ConvertTerbilang (n%1000000)
        elif n <1000000000000:
            Hasil = Procedure.ConvertTerbilang (n/1000000000) + " Milyar " + Procedure.ConvertTerbilang (n%1000000000)
        elif n <1000000000000000:
            Hasil = Procedure.ConvertTerbilang (n/1000000000000) + " Triliyun " + Procedure.ConvertTerbilang (n%1000000000000)
        elif n == 1000000000000000:
            Hasil = "Satu Kuadriliun"
        else:
            Hasil = "Angka Hanya Sampai Satu Kuadriliun"

        return Hasil