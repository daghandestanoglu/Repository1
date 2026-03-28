import time
import os

d = open("deneme4.txt","w")
d.write("Dahan\n")
d.write("Giray\n")
d.write("Destan\n")
d.close()  # Always close the file first

time.sleep(5)  # Wait 5 seconds

os.remove("deneme4.txt")  # Delete the file
