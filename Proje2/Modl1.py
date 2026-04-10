import Proje2.Modl4
def UrunAra():
    aranan = input("Aranacak ürünün ismi(Boşluk bırakırsanız hepsini listeler):").strip().lower()
    Urunler= Proje2.Modl4.Urunoku()
    if not Urunler:
        print("Envanter boş.")
        return
    sonuclar = []
    for k in Urunler:
        if aranan.lower() in k["ad"].lower():
            sonuclar.append(k)
    if not sonuclar:
        print(f"{aranan} ile eşleşen bulunamadı.")
    else:
        print(f"\n{'-'*35}")
        print(f"{'Ad':20}{'Sayı'}")
        print(f"{'-'*35}")
        for k in sonuclar:
            print(f"{k['ad']:<20}{k['sayi']}")
        print(f"{'-'*35}")
        print(f"Toplam {len(sonuclar)} ürün.")
