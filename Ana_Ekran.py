# -*- coding: utf-8 -*-
import Moduller.SubInterface1          # sadece tanım, çalıştırılmaz
# import Moduller.SubInterface2        # gerekirse aynı şekilde
# import Moduller.SubInterface3        # gerekirse aynı şekilde

def ana_menu():
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
            Moduller.SubInterface1.AltMenu1()   # menüyü çalıştır
        elif secim == "2":
            print("Oyunlar seçtiniz.")
            # Moduller.SubInterface2.some_func()
        elif secim == "3":
            print("Çizimler seçtiniz.")
            # Moduller.SubInterface3.some_func()
        elif secim == "0":
            print("Çıkış yapılıyor...")
            break                               # döngüden çık, program biter
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")
            # döngü otomatik tekrarla, menü tekrar gösterilir

# ------------------- Çalıştırma -------------------
if __name__ == "__main__":
    ana_menu()