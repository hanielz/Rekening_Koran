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

                if auxtrc in ('8518','8506') :
                    desk_tran = 'TRANSFER ' + desk_tran
                    
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