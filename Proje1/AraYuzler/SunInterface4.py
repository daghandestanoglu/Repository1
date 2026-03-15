from datetime import datetime
from zoneinfo import ZoneInfo
import time
import subprocess
import sys

import subprocess
import sys

def tzdata_yukle():
    try:
        import tzdata
        return True
    except ImportError:
        cevap = input("tzdata paketi bulunamadi. Yuklemek ister misiniz? (Y/n): ")
        if cevap.lower().strip() == "y":
            print("Yukleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tzdata"])
            print("Yukleme tamamlandi.")
            return True
        else:
            print("Yukleme iptal edildi. Dunya saatleri calisмayacak.")
            return False



def dunya_saatleri():
    if not tzdata_yukle():
        return

    cities = {
        "Ankara":    "Europe/Istanbul",
        "İstanbul":  "Europe/Istanbul",
        "Londra":    "Europe/London",
        "New York":  "America/New_York",
        "Los Angeles": "America/Los_Angeles",
        "São Paulo": "America/Sao_Paulo",
        "Dubai":     "Asia/Dubai",
        "Moskova":   "Europe/Moscow",
        "Tokyo":     "Asia/Tokyo",
        "Sidney":    "Australia/Sydney",
    }

    print("=" * 40)
    print(f"{'DÜNYA SAATLERİ':^40}")
    print("=" * 40)

    for city, tz in cities.items():
        now = datetime.now(ZoneInfo(tz))
        saat = now.strftime("%H:%M:%S")
        tarih = now.strftime("%d/%m/%Y")
        print(f"  {city:<14} →  {saat}   {tarih}")

    print("=" * 40)
    time.sleep(0.8)


def kronometre():
    print("Kronometreyi baslatmak icin Enter'a bas...")
    input()
    
    baslangic = time.time()
    print("Kronometre basladi! Durdurmak icin Ctrl+C'ye bas.")
    
    try:
        while True:
            gecen = time.time() - baslangic
            dakika = int(gecen // 60)
            saniye = int(gecen % 60)
            milisaniye = int((gecen % 1) * 100)
            print(f"\r Gecen sure: {dakika:02}:{saniye:02}.{milisaniye:02}", end="")
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        gecen = time.time() - baslangic
        dakika = int(gecen // 60)
        saniye = int(gecen % 60)
        milisaniye = int((gecen % 1) * 100)
        print(f"\n\nSonuc: {dakika:02}:{saniye:02}.{milisaniye:02}")
        print("Kronometre durduruldu.")
        
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getwch()
        
    time.sleep(1.2)


def zamanlayici():
    print("ZAMANLAYICI")
    print("-" * 30)
    
    dakika = int(input("Dakika girin: "))
    saniye = int(input("Saniye girin: "))
    
    toplam_saniye = dakika * 60 + saniye
    
    if toplam_saniye <= 0:
        print("Gecerli bir sure girin!")
        return
    
    print("\nZamanlayici basladi! Durdurmak icin Ctrl+C'ye bas.")
    print("-" * 30)
    
    try:
        for kalan in range(toplam_saniye, 0, -1):
            dk = kalan // 60
            sn = kalan % 60
            print(f"\r Kalan sure: {dk:02}:{sn:02}", end="")
            time.sleep(1)
        
        print("\n" + "=" * 30)
        print("SURE DOLDU!")
        print("=" * 30)
        time.sleep(0.8)
    
    except KeyboardInterrupt:
        print("\n\nZamanlayici iptal edildi.")
        return



     #KOD BAŞLANGIÇ#
def AltMenu4():
    while True:
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
        elif secim == "1":
            print("Dünya saatini seçtiniz.")
            dunya_saatleri()
        elif secim == "2":
            print("Kronometreyi seçtiniz.")
            kronometre()
        elif secim == "3":
            print("Zamanlıyıcı alarmı seçtiniz.")
            zamanlayici()
        else:
            print("Geçersiz seçim.")
            AltMenu4()
            return
if __name__ == "__main__":
    AltMenu4()