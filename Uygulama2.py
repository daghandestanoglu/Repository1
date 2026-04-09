
import Proje2.Modl2
def AnaMenu():
    while True:
        print("╔════════════════════════╗")
        print("║   Envanter Uygulaması  ║")
        print("╠════════════════════════╣")
        print("║ 1-) Ürün Ekle          ║")
        print("║ 2-) Ürün Çıkar         ║")
        print("║ 3-) Ürün Ara / Listele ║")
        print("║ 4-) Ürün Güncelle      ║")
        print("║                        ║")
        print("║                        ║")
        print("║ 0-) Çıkış              ║")
        print("╚════════════════════════╝")
        secim = input("Seçiminiz nedir?:").strip()
        if secim == "1":
            Proje2.Modl2.UrunEk()
        elif secim == "2":
            #
        elif secim == "3":
            #
        elif secim == "4":
            #
        elif secim == "0":
            #
        else:
            print("Geçersiz Sayı girdiniz, bir daha deneyin.")

if  __name__ == "__main__":
    Anamenu()