def Ana_Ekran():
    print("╔════════════════════════╗")
    print("║        UYGULAMA        ║")
    print("╠════════════════════════╣")
    print("║ 1-) Hesap Makinası     ║")
    print("║ 2-) Oyunlar            ║")
    print("║ 3-) Çizimler           ║")
    print("║                        ║")
    print("║                        ║")
    print("║                        ║")
    print("║                        ║")
    print("║ 0-) Çıkış              ║")
    print("╚════════════════════════╝")
    print("Seçiminiz nedir?: ", end="")
    Secim = str(input())
    print(f"{Secim}. seçeneği seçtiniz.")
    if Secim == "1":
        print("Hesap Makinası seçtiniz.")
        import Moduller.SubInterface1
    elif Secim == "2":
        print("Oyunlar seçtiniz.")
        import Moduller.SubInterface2
    #elif Secim == "3":
        #print("Çizimler seçtiniz.")
        #import Moduller.SubInterface3   
    elif Secim == "0":
        print("Çıkış yapılıyor...")
    else:
        print("Geçersiz seçim. Lütfen tekrar deneyin.")
    # 201 ╔
    # 205 ═
    # 187 ╗
    # 186 ║
    # 200 ╚
    # 188 ╝
    # 185 ╣
     # 204 ╠
