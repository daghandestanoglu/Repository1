import Proje2.Urunara
import Proje2.Urunyaz
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
    
    Urunler=Proje2.Urunara.UrunAra()
    
    for urun in Urunler:
        if urun["ad"].lower()== Ad:
            print("Ürün ismi zaten girilmiş, değer değiştrimek için Ürün Güncelle'yi kullanın")
    Urunler.append({"ad":Ad,"sayi":sayi})
    Proje2.Urunyaz.UrunYaz(Urunler)
    print(f"{Ad} envantere eklendi.")