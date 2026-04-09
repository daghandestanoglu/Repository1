def Urunoku():
    DOSYA_ADI = "envanter.txt"
    urunler=[]
    try:
        with open(DOSYA_ADI,r, encoding="utf-8") as f:
            for satir in f:
                satir=satir.strip()
                if satir:
                    aD, sayi = satir.split(",",1)
                    urunler.append({"ad":aD,"sayi":sayi})
    except FileNotFoundError:
        pass
    return urunler