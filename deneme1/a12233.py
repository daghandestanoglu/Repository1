def topla(*toplancaklar):
    sum=0
    for k in toplancaklar:
        sum=sum+k
    return sum 
def menu_yap(*girdi):
    uzun=0
    for a in girdi:
        if uzun<len(a):
            uzun=len(a)
    print(f"{'-'*(uzun+2)}")
    for k in girdi:
        print(f"|{k}",end="")
        print(" "*(uzun-len(k)),end="")
        print("|")
menu_yap('abc','absadaf','gafa',"ömjhgfdmnbvcx")