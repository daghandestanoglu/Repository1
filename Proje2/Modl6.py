import Proje2.Modl4
import Proje2.Modl3

def UrunGuncelle():
    ad=input("Güncellenecek ürünün adı:").strip()
    urunler=Proje2.Modl4.Urunoku()
    guncel=False
    for urun in urunler:
        if urun['ad'].lower()==ad.lower():
            print(f"Güncel sayı:{urun['sayi']}")
            try:
                yeni_sayi  =  int(input("Yeni ürün sayısı: ").strip())
                if yeni_sayi <=0:
                    print("Lütfen geçerli bir değer giriniz.")
                    return   
            except ValueError:
                print("Lütfen geçerli bir değer giriniz.")
                return
            
            urun["sayi"]=yeni_sayi
            guncel=True
            break
    if guncel:
        Proje2.Modl3.UrunYaz(urunler)
        print(f"{ad} sayısı güncellendi.")
    else:
        print(f"{ad} bulunamadı.")

