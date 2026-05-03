import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from collections import deque

# --- Ayarlar ---
max_len = 500
zaman_dizisi = deque(maxlen=max_len)
giris_dizisi = deque(maxlen=max_len)
vco_dizisi = deque(maxlen=max_len)
hata_dizisi = deque(maxlen=max_len)

# --- Baslangic Degerleri ---
vco_fazi = 0.0
integral_toplami = 0.0
t = 0

# --- Grafik Hazirligi ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
plt.subplots_adjust(bottom=0.3, hspace=0.4)

line_giris, = ax1.plot([], [], lw=2, label='Giris Sinyali', color='blue')
line_vco, = ax1.plot([], [], lw=2, label='VCO (Takipci)', color='orange', alpha=0.7)
line_hata, = ax2.plot([], [], lw=2, label='Faz Hatasi', color='red')

ax1.set_ylim(-1.5, 1.5)
ax1.legend(loc='upper right')
ax1.set_title("Sinyal Takibi (Zaman Duzlemi)")
ax1.grid(True, alpha=0.3)

ax2.set_ylim(-1.5, 1.5)
ax2.legend(loc='upper right')
ax2.set_title("Faz Hatasi (Ideal Dedektor)")
ax2.grid(True, alpha=0.3)

# --- Slider Kontrolleri ---
axfreq = plt.axes([0.2, 0.15, 0.65, 0.03])
axkp = plt.axes([0.2, 0.1, 0.65, 0.03])
axki = plt.axes([0.2, 0.05, 0.65, 0.03])

sfreq = Slider(axfreq, 'Frekans', 0.05, 0.2, valinit=0.1)
skp = Slider(axkp, 'Kp (Hiz)', 0.001, 1.0, valinit=0.1)
ski = Slider(axki, 'Ki (Kararli)', 0.0, 0.1, valinit=0.005)

def update(frame):
    global vco_fazi, integral_toplami, t
    
    # Parametreleri sliderdan oku
    f_in = sfreq.val
    kp = skp.val
    ki = ski.val
    
    # Giris sinyali ve fazi
    giris_fazi = f_in * t
    giris_sinyali = np.sin(giris_fazi)
    
    # VCO (Takipci) sinyali
    vco_sinyali = np.sin(vco_fazi)
    
    # Ideal Faz Dedektoru (Faz farkini dogrudan hesaplar)
    ham_hata = np.sin(giris_fazi - vco_fazi)
    
    # PI Kontrolcu (Dongu Filtresi)
    integral_toplami += ham_hata
    frekans_duzeltme = (kp * ham_hata) + (ki * integral_toplami)
    
    # VCO Faz Guncelleme
    # Temel frekans (f_in) + hata duzeltmesi
    vco_fazi += f_in + frekans_duzeltme
    
    # Verileri sakla
    zaman_dizisi.append(t)
    giris_dizisi.append(giris_sinyali)
    vco_dizisi.append(vco_sinyali)
    hata_dizisi.append(ham_hata)
    
    t += 1
    
    # Ekseni kaydir
    ax1.set_xlim(zaman_dizisi[0], zaman_dizisi[-1] if len(zaman_dizisi) > 1 else max_len)
    ax2.set_xlim(zaman_dizisi[0], zaman_dizisi[-1] if len(zaman_dizisi) > 1 else max_len)
    
    # Cizgileri guncelle
    line_giris.set_data(zaman_dizisi, giris_dizisi)
    line_vco.set_data(zaman_dizisi, vco_dizisi)
    line_hata.set_data(zaman_dizisi, hata_dizisi)
    
    return line_giris, line_vco, line_hata

# Simulasyonu baslat (interval=1 en yuksek hizdir)
ani = FuncAnimation(fig, update, interval=1, blit=False, cache_frame_data=False)
plt.show()