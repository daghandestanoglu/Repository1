def UrunYaz(urunler):
    DOSYA_ADI = "envanter.txt"
    with open("envanter.txt","w",encoding="utf-8") as d:
        for urun in urunler:
            d.write(f"{urun['ad']},{urun['sayi']}\n")
            