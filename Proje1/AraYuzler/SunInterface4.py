from datetime import datetime
from zoneinfo import ZoneInfo
import time

def dunya_saatleri():
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
    print("Kronometreyi başlatmak için Enter'a bas...")
    input()
    
    baslangic = time.time()
    print("Kronometre başladı! Durdurmak için Enter'a bas...")
    input()
    
    sure = time.time() - baslangic
    
    dakika = int(sure // 60)
    saniye = int(sure % 60)
    milisaniye = int((sure % 1) * 100)
    
    print(f"Geçen süre: {dakika:02}:{saniye:02}.{milisaniye:02}")
    time.sleep(0.8)



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
        else:
            print("Geçersiz seçim.")
            AltMenu4()
            return
if __name__ == "__main__":
    AltMenu4()