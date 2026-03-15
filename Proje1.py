# -*- coding: utf-8 -*-
import Proje1.AraYuzler.SubInterface1          # sadece tanım, çalıştırılmaz
import Proje1.AraYuzler.SubInterface2        # gerekirse aynı şekilde
import Proje1.AraYuzler.SubInterface3    # gerekirse aynı şekilde

def AnaMenu():
    while True:                         # ← ana menü döngüsü
        print("╔════════════════════════╗")
        print("║        UYGULAMA        ║")
        print("╠════════════════════════╣")
        print("║ 1-) Hesap Makinası     ║")
        print("║ 2-) Oyunlar            ║")
        print("║ 3-) Çizimler           ║")
        print("║                        ║")
        print("║                        ║")
        print("║                        ║")
        print("║ 0-) Çıkış              ║")
        print("╚════════════════════════╝")

        secim = input("Seçiminiz nedir?: ")
        print(f"{secim}. seçeneği seçtiniz.")

        if secim == "1":
            print("Hesap Makinası seçtiniz.")
            AraYuzler.SubInterface1.AltMenu1()   # menüyü çalıştır
        elif secim == "2":
            print("Oyunlar seçtiniz.")
            AraYuzler.SubInterface2.AltMenu2()
        elif secim == "3":
            print("Çizimler seçtiniz.")
            AraYuzler.SubInterface3.AltMenu3()
        elif secim == "0":
            print("Çıkış yapılıyor...")
            break                               # döngüden çık, program biter
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")
            # döngü otomatik tekrarla, menü tekrar gösterilir

# ------------------- Çalıştırma -------------------
if __name__ == "__main__":
    AnaMenu()