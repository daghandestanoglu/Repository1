import random as r
s=0
for aa in range(100000):
    x=r.randint(1,100)
    s=s+x
    # print(x)
print(f"Ortalama: {s/100000}")