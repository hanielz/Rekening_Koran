from datetime import datetime
tgl_awal ="20220616"
tgl_akhir ="20220630"

def convertJulianDate(self,date,*argv):
    date=datetime.strptime(date,'%Y%m%d')
    date=int(str(date)[:4]+str(date.strftime('%j')))
    
    for number in argv:
        date += number
    return date

julianDate = convertJulianDate(tgl_awal,tgl_akhir)


print(julianDate)
