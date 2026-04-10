import Proje2.Modl4
import Proje2.Modl3

def Urunsil():
    ad = input("Silinecek ürünün adı:").strip()
    urunler = Proje2.Modl4.Urunoku()
    Yeniliste=[]
    for k in urunler:
        if k['ad'].lower()!= ad.lower():
            Yeniliste.append(k)
    if len(Yeniliste)==len(urunler):
        print("Silinecek kişi bulunamadı.")
    else:
        Proje2.Modl3.UrunYaz(Yeniliste)
        print(f"{ad} başarıyla silindi.")
    

