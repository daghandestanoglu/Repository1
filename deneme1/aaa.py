import time
import os

d = open("deneme4.txt","w")
d.write("Dahan\n")
d.write("Giray\n")
d.write("Destan\n")
d.close()
d = open("deneme4.txt","r")
print(d.read())
d.close()
time.sleep(3)  # Always close the file first
d = open("deneme4.txt","a")
d.write("Ekleme?\n")
d.close()
d = open("deneme4.txt","r")
print(d.read())
d.close()
with open("deneme4.txt","a") as d:
    d.write(input("Bi şeyler yaz:").strip().lower())
with open("deneme4.txt","r") as d:
    print(d.read())
    d.seek(0)
    for i, satir in enumerate(d, start=1):  # enumerate satır numarası verir
        if "ali" in satir.lower():
            print(f"Bulundu: '{satir.strip()}'  -> Satır numarası: {i}")  
time.sleep(3)  # Wait 5 seconds


os.remove("deneme4.txt")  # Delete the file
