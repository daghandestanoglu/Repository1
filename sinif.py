d=open("Deneme1.txt","w",encoding="utf-8")
isim=input("İsim:").strip().lower()
d.write(f"Ad:\t{isim}")
d.write("\n")

Soyad=input("Soyad:").strip().lower()
d.write(f"Soyad:\t{Soyad}")
d.write("\n")

Numara=input("Numara:").strip().lower()
d.write(f"Numara:\t{Numara}")
d.write("\n")
d.close()