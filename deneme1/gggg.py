import numpy as np
import matplotlib.pyplot as plt

# 1. PARAMETRELER
fs = 1000              # Örnekleme frekansı (Hz)
f = 50                 # Sinyal frekansı (50 Hz)
# 0'dan 0.1 saniyeye kadar zaman vektörü oluşturma
# (MATLAB'deki 0:1/Fs:0.1 ifadesinin karşılığı)
t = np.arange(0, 0.1 + 1/fs, 1/fs) 

# 2. REEL VE KOMPLEKS SİNYAL ÜRETİMİ
x_real = np.sin(2 * np.pi * f * t)
# Python'da sanal sayı birimi 'j' ile ifade edilir (1j)
x_complex = np.exp(1j * 2 * np.pi * f * t)

# 3. ZAMAN DOMAİNİ GRAFİKLERİ
plt.figure(figsize=(10, 8))

# Reel Sinyal
plt.subplot(2, 1, 1)
plt.plot(t, x_real, 'b', linewidth=1.5)
plt.title('Reel Sinyal Zaman Domaini: sin(2π f t)')
plt.xlabel('Zaman (s)')
plt.ylabel('Genlik')
plt.grid(True)

# Kompleks Sinyal (Reel ve İmajiner kısımlar)
plt.subplot(2, 1, 2)
plt.plot(t, x_complex.real, 'b', label='Reel Kısım (Cos)', linewidth=1.5)
plt.plot(t, x_complex.imag, 'r--', label='İmajiner Kısım (Sin)', linewidth=1.5)
plt.title('Kompleks Sinyal Zaman Domaini: e^{j 2π f t}')
plt.xlabel('Zaman (s)')
plt.ylabel('Genlik')
plt.legend()
plt.grid(True)
plt.tight_layout()

# 4. FREKANS DOMAİNİ GRAFİKLERİ (FFT)
n = len(t)
# Frekans eksenini oluşturma
f_axis = np.fft.fftshift(np.fft.fftfreq(n, 1/fs))

# FFT İşlemleri
x_real_fft = np.fft.fftshift(np.fft.fft(x_real))
x_complex_fft = np.fft.fftshift(np.fft.fft(x_complex))

plt.figure(figsize=(10, 8))

# Reel Sinyal FFT
plt.subplot(2, 1, 1)
plt.plot(f_axis, np.abs(x_real_fft)/n, 'b', linewidth=1.5)
plt.title('Reel Sinyal Frekans Spektrumu (Çift Taraflı)')
plt.xlabel('Frekans (Hz)')
plt.ylabel('Genlik')
plt.grid(True)

# Kompleks Sinyal FFT
plt.subplot(2, 1, 2)
plt.plot(f_axis, np.abs(x_complex_fft)/n, 'r', linewidth=1.5)
plt.title('Kompleks Sinyal Frekans Spektrumu (Tek Taraflı)')
plt.xlabel('Frekans (Hz)')
plt.ylabel('Genlik')
plt.grid(True)
plt.tight_layout()

plt.show()