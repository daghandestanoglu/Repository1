import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

# Deney Verileri
R_L = [100, 200, 300, 330, 400, 500, 600, 700]
P_L = [27.56, 36.99, 38.99, 39.35, 39.20, 37.85, 36.50, 34.44]

# Eğriyi yumuşatmak için spline kullanımı
R_L_smooth = np.linspace(min(R_L), max(R_L), 300)
spl = make_interp_spline(R_L, P_L, k=3)
P_L_smooth = spl(R_L_smooth)

plt.figure(figsize=(8, 5))
plt.plot(R_L_smooth, P_L_smooth, color='blue', label='Power Curve')
plt.scatter(R_L, P_L, color='red', zorder=5, label='Measured Data Points')

# Maksimum noktayı işaretleme
plt.annotate('Max Power Transfer\n(330 Ω, 39.35 mW)', xy=(330, 39.35), xytext=(400, 32),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.title("Power Delivered to Load vs. Load Resistance")
plt.xlabel("Load Resistance (R_L) [Ω]")
plt.ylabel("Power (P_L) [mW]")
plt.grid(True)
plt.legend()
plt.show()