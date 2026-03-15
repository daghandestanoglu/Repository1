def AltMenu4()
    print("╔════════════════════════╗")
    print("║          Saat          ║")
    print("╠════════════════════════╣")
    print("║ 1-) Dünya Saati        ║")
    print("║ 2-) Kronometre         ║")
    print("║ 3-) Zamanlıyıcı Alarm  ║")
    print("║                        ║")
    print("║                        ║")
    print("║                        ║")
    print("║  0-Geri Dön            ║")
    print("╚════════════════════════╝")
    print("Seçiminiz nedir?: ", end="")
    secim = input()
    print(f"{secim}. seçeneği seçtiniz.")
    if secim == "0":
        print("Ana menüye dönülüyor...")
        return "back_to_main"
    return