import Proje2.Modl4
import Proje2.Modl3
def UrunEk():
   
    Ad  =  input("Ürün adı: ").strip().lower()
    try:
        sayi  =  int(input("Ürün sayısı: ").strip())
    except ValueError:
        print("Lütfen geçerli bir değer giriniz.")
        return
    if not Ad or not sayi:
        print("Ad ve sayı boş bırakılamaz.")
        return
    if sayi <= 0:
        print("Sayı sıfırdan büyük olmalı.")
        return
    
    Urunler=Proje2.Modl4.Urunoku()
    
    for urun in Urunler:
        if urun["ad"].lower()== Ad:
            print("Ürün ismi zaten girilmiş, değer değiştrimek için Ürün Güncelle'yi kullanın")
            return
    Urunler.append({"ad":Ad,"sayi":sayi})
    Proje2.Modl3.UrunYaz(Urunler)
    print(f"{Ad} envantere eklendi.")