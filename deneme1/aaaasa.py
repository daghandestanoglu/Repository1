"""
📒 Telefon Rehberi - TXT Dosyası ile
Dosya işlemlerini öğrenmek için basit bir proje.

Her satırın formatı: Ad Soyad,Numara
Örnek: Ahmet Yılmaz,05551234567
"""

DOSYA_ADI = "rehber.txt"


# ─────────────────────────────────────────
# YARDIMCI FONKSİYONLAR (Dosya okuma/yazma)
# ─────────────────────────────────────────

def kisileri_oku():
    """
    TXT dosyasını okuyup sözlük listesi döndürür.
    Dosya yoksa boş liste döner.
    """
    kisiler = []
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()          # Baş/sondaki boşlukları temizle
                if satir:                       # Boş satırları atla
                    ad, numara = satir.split(",", 1)  # Virgülden böl
                    kisiler.append({"ad": ad, "numara": numara})
    except FileNotFoundError:
        pass  # Dosya yoksa sorun değil, boş liste döner
    return kisiler


def kisileri_yaz(kisiler):
    """
    Sözlük listesini alıp TXT dosyasına yazar.
    Dosyayı tamamen sıfırdan yazar (w modu).
    """
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        for kisi in kisiler:
            f.write(f"{kisi['ad']},{kisi['numara']}\n")


# ─────────────────────────────────────────
# ANA FONKSİYONLAR
# ─────────────────────────────────────────

def kisi_ekle():
    """Yeni kişi ekler ve dosyaya kaydeder."""
    ad = input("Ad Soyad: ").strip()
    numara = input("Telefon numarası: ").strip()

    if not ad or not numara:
        print("❌ Ad ve numara boş bırakılamaz.")
        return

    kisiler = kisileri_oku()

    # Aynı isim zaten var mı?
    for kisi in kisiler:
        if kisi["ad"].lower() == ad.lower():
            print(f"⚠️  '{ad}' zaten rehberde mevcut.")
            return

    kisiler.append({"ad": ad, "numara": numara})
    kisileri_yaz(kisiler)
    print(f"✅ {ad} rehbere eklendi.")


def kisi_sil():
    """İsme göre kişiyi siler."""
    ad = input("Silinecek kişinin adı: ").strip()
    kisiler = kisileri_oku()

    yeni_liste = [k for k in kisiler if k["ad"].lower() != ad.lower()]

    if len(yeni_liste) == len(kisiler):
        print(f"❌ '{ad}' bulunamadı.")
    else:
        kisileri_yaz(yeni_liste)
        print(f"🗑️  '{ad}' rehberden silindi.")


def kisi_ara():
    """
    İsme göre arama yapar.
    Boş bırakılırsa tüm rehberi listeler.
    """
    aranan = input("Aranacak isim (boş bırakırsan herkesi listeler): ").strip()
    kisiler = kisileri_oku()

    if not kisiler:
        print("📭 Rehber boş.")
        return

    # Filtrele: aranan boşsa hepsini göster, değilse isimde geçenleri göster
    sonuclar = [
        k for k in kisiler
        if aranan.lower() in k["ad"].lower()
    ]

    if not sonuclar:
        print(f"❌ '{aranan}' ile eşleşen kimse bulunamadı.")
    else:
        print(f"\n{'─'*35}")
        print(f"{'Ad Soyad':<20} {'Numara'}")
        print(f"{'─'*35}")
        for k in sonuclar:
            print(f"{k['ad']:<20} {k['numara']}")
        print(f"{'─'*35}")
        print(f"Toplam: {len(sonuclar)} kişi\n")


def kisi_guncelle():
    """Mevcut bir kişinin numarasını günceller."""
    ad = input("Güncellenecek kişinin adı: ").strip()
    kisiler = kisileri_oku()

    guncellendi = False
    for kisi in kisiler:
        if kisi["ad"].lower() == ad.lower():
            print(f"Mevcut numara: {kisi['numara']}")
            yeni_numara = input("Yeni numara: ").strip()
            if yeni_numara:
                kisi["numara"] = yeni_numara
                guncellendi = True
            break

    if guncellendi:
        kisileri_yaz(kisiler)
        print(f"✅ '{ad}' güncellendi.")
    else:
        print(f"❌ '{ad}' bulunamadı.")


# ─────────────────────────────────────────
# ANA MENÜ
# ─────────────────────────────────────────

def menu():
    """Programın ana döngüsü."""
    print("\n📒 Telefon Rehberine Hoş Geldiniz!")

    while True:
        print("\n─── MENÜ ───────────────")
        print("1. Kişi Ekle")
        print("2. Kişi Sil")
        print("3. Kişi Ara / Listele")
        print("4. Kişi Güncelle")
        print("5. Çıkış")
        print("────────────────────────")

        secim = input("Seçiminiz (1-5): ").strip()

        if secim == "1":
            kisi_ekle()
        elif secim == "2":
            kisi_sil()
        elif secim == "3":
            kisi_ara()
        elif secim == "4":
            kisi_guncelle()
        elif secim == "5":
            print("👋 Görüşürüz!")
            break
        else:
            print("⚠️  Geçersiz seçim, 1-5 arası bir sayı girin.")


# Programı başlat
if __name__ == "__main__":
    menu()