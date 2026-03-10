print("Kullanılacak sayı adetini girin:")
adet=int(input())
sayilar=[]
for i in range (adet):
    sayi=float(input(f"Lütfen {i+1}. sayıyı girin:"))
    sayilar.append(sayi)
