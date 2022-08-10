print ('TUGAS PROGRAM TERBILANG')
print ('PRAKTIKUM PEMROGRAMAN KOMPUTER')
print ('NAMA : MUHAMMAD NURFAIZ')
print ('NIM  : D600160110')
print ('Fakultas Teknik Jurusan Teknik Industri')
print ('UNIVERSITAS MUHAMMADIYAH SURAKARTA')
print (' ')
def Terbilang(bil):
    angka = ["","Satu","Dua","Tiga","Empat","Lima","Enam",
             "Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
    Hasil = " "
    n = int(bil)
    if n>= 0 and n <= 11:
        Hasil = angka[n]
    elif n <20:
        Hasil = Terbilang (n-10) + " Belas "
    elif n <100:
        Hasil = Terbilang (n/10) + " Puluh " + Terbilang (n%10)
    elif n <200:
        Hasil = " Seratus " + Terbilang (n-100)
    elif n <1000:
        Hasil = Terbilang (n/100) + " Ratus " + Terbilang (n%100)
    elif n <2000:
        Hasil = " Seribu " + Terbilang (n-1000)
    elif n <1000000:
        Hasil = Terbilang (n/1000) + " Ribu " + Terbilang (n%1000)
    elif n <1000000000:
        Hasil = Terbilang (n/1000000) + " Juta " + Terbilang (n%1000000)
    elif n <1000000000000:
        Hasil = Terbilang (n/1000000000) + " Milyar " + Terbilang (n%1000000000)
    elif n <1000000000000000:
        Hasil = Terbilang (n/1000000000000) + " Triliyun " + Terbilang (n%1000000000000)
    elif n == 1000000000000000:
        Hasil = "Satu Kuadriliun"
    else:
        Hasil = "Angka Hanya Sampai Satu Kuadriliun"

    return Hasil
a=1
while a!= 0:
    a = input('Masukan angka dari 1 sd 1.000.000.000.000.000(0 untuk keluar): ')
    huruf = Terbilang(a)
    print (' Terbilang ---- '+huruf+ ' Rupiah ----')
    continue