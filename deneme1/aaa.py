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
time.sleep(5)  # Always close the file first
d = open("deneme4.txt","a")
d.write("Ekleme?\n")
d.close()
d = open("deneme4.txt","r")
print(d.read())
d.close()
time.sleep(5)  # Wait 5 seconds

os.remove("deneme4.txt")  # Delete the file
