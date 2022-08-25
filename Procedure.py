#from Models import Models
from db import Config
class Procedure(object) : 

    _Singleton = None
    desk_tran = ''

    #constructor contain connection 
    def __init__(self):
        Procedure._Singleton = Config()

    def getremark(self,auxtrc, trancd,eftacc, trremk) : 
        #auxtrc,trancd ,eftacc, trremk
    
        #variable local 
        desk_tran = ''
        tlxaft = ''

        
        getTrancd = Procedure._Singleton.trancdQuery(trancd) #get TRANCD form DDPAR3
        getTltxds = Procedure._Singleton.tltxdsQuery(auxtrc)  #Gget tltxds from AS400_TLTX
        getTltxaft = Procedure._Singleton.tltxaftQuery(auxtrc)  #Gget tltxaft from AS400_TLTX

        print("auxtrc :", auxtrc)
        print("trancd :",trancd)
        print("eftacc :" ,eftacc)
        print("trremk :", trremk)

        print("get TRANCD form DDPAR3 : ", getTrancd)
        print("Gget tltxds from AS400_TLTX : ", getTltxds)
        print("Gget tltxaft from AS400_TLTX : ",getTltxaft)

    
        if (auxtrc != "" ):  
            lxaft= getTltxaft  

            #RANGE to STRING
            # Procedure.rangeString(self,auxtrc )
            
        
            if (tlxaft =='A1' or auxtrc in('0688','0689') and Procedure.rangeString(self,auxtrc,716,712 ) == True):
                desk_tran = getTltxds
                if trancd == getTrancd :
                    desk_tran = trremk
                else :                              
                    desk_tran = getTltxds

                #--SELECT @DESK_TRAN=''

                # IF (@AUXTRC BETWEEN '8500' AND '8699') OR (@AUXTRC BETWEEN '2762' AND '2765')
				# BEGIN
				# @DESK_TRAN= SUBSTRING(@TRREMK,1,20) --REMARK1

				# @DESK_TRAN= @DESK_TRAN + SUBSTRING(@TRREMK,21,LEN(@TRREMK)) --REMARK2

                # IF (@AUXTRC = '2501')
				# BEGIN
				# 	 @DESK_TRAN = 'PENARIKAN DARI ATM ' + @DESK_TRAN
				# END
								
				# IF (@AUXTRC IN ('8518','8506'))
				# BEGIN
				# 	@DESK_TRAN = 'TRANSFER ' + @DESK_TRAN
				# END
						
			
				# IF (@AUXTRC = '9996')
				# BEGIN
				# 	 @DESK_TRAN = 'PENARIKAN TUNAI ATM BANK LAIN ' + @DESK_TRAN
				# END
				
						
				# IF (@AUXTRC = '8522')
				# BEGIN
				# 	 @DESK_TRAN = 'PEMBAYARAN ' + @DESK_TRAN
				# END
            else : #else of tlxaft =='A1'
                if (trremk !='') : 
                    desk_tran=trremk
                #else :    
		            #desk_tran=getTltxds	
        return desk_tran

    def rangeString(self,x,startRange, endRange) :
        for i in range(startRange, endRange):
            convertToString=str(i).zfill(4)
            print(convertToString, 'auxtrc : ', x)
            if convertToString == x :return True 
            else : return False