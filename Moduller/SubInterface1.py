print("╔════════════════════════╗")
print("║     Hesap Makinesi     ║")
print("╠════════════════════════╣")
print("║ 1-) Toplama            ║")
print("║ 2-) Çıkarma            ║")
print("║ 3-) Bölme              ║")
print("║ 4-) Çarpma             ║")
print("║                        ║")
print("║                        ║")
print("║                        ║")
print("║  0-Geri Dön            ║")
print("╚════════════════════════╝")
x=float(input("Birinci sayıyı giriniz: "))
y=float(input("İkinci sayıyı giriniz: "))
print("Seçiminiz nedir?: ",end="")
Secim1= input()
print(f"{Secim1}. seçeneği seçtiniz.")
if Secim1 == "1":
    print(f"{x} + {y} = {x+y}")
elif Secim1 == "2":
    print(f"{x} - {y} = {x-y}")
elif Secim1 == "3":
    if y != 0:
        print(f"{x} / {y} = {x/y}")
    else:
        print("Bir sayı sıfıra bölünemez.")
elif Secim1 == "4":
    print(f"{x} * {y} = {x*y}")
elif Secim1 == "0":
    print("Ana menüye dönülüyor...")
    import Ana_Ekran
else:
    print("Geçersiz seçim. Lütfen tekrar deneyin.")
    ##import Moduller.SubInterface1
    