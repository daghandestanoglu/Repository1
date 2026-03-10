def AltMenu1():
    print("╔════════════════════════╗")
    print("║     Hesap Makinesi     ║")
    print("╠════════════════════════╣")
    print("║ 1-) Toplama            ║")
    print("║ 2-) Çıkarma            ║")
    print("║ 3-) Bölme              ║")
    print("║ 4-) Çarpma             ║")
    print("║ 5-) Üs alma            ║")
    print("║                        ║")
    print("║  0-Geri Dön            ║")
    print("╚════════════════════════╝")

    x = float(input("Birinci sayıyı giriniz: "))
    y = float(input("İkinci sayıyı giriniz: "))
    print("Seçiminiz nedir?: ", end="")
    secim = input()
    print(f"{secim}. seçeneği seçtiniz.")

    if secim == "1":
        print(f"{x} + {y} = {x+y}")
    elif secim == "2":
        print(f"{x} - {y} = {x-y}")
    elif secim == "3":
        if y != 0:
            print(f"{x} / {y} = {x/y}")
        else:
            print("Bir sayı sıfıra bölünemez.")
    elif secim == "4":
        print(f"{x} * {y} = {x*y}")
    elif secim == "5":
        print(f"{x} ^ {y} = {x**y}")
    elif secim == "0":
        print("Ana menüye dönülüyor...")
        return "back_to_main"
    else:
        print("Geçersiz seçim. Tekrar deneyin.")
        AltMenu1()          # aynı fonksiyonu tekrar çalıştır
        return

# Çalıştırma
if __name__ == "__main__":
    AltMenu1()