from django.shortcuts import render,redirect
from .models import Urun

def dashboard(request):
    urunler = Urun.objects.all()
    toplam_urun_sayisi = urunler.count()
    
    context = {
        'toplam_urun': toplam_urun_sayisi,
        'urunler': urunler,  # Tüm ürün listesini şablona fırlatıyoruz
    }
    return render(request, 'dashboard.html', context)
# DOĞRU SATIR
def urun_ekle(request):
    if request.method == 'POST':
        urun_adi = request.POST.get('urun_adi').strip().lower()
        urun_sayisi = request.POST.get('urun_sayisi')
        
        if urun_adi and urun_sayisi:
            Urun.objects.create(ad=urun_adi, sayi=int(urun_sayisi))
            return redirect('dashboard')
            
    return render(request, 'urun_ekle.html')
            
    return render(request, 'urun_ekle.html')
def urun_sil(request, urun_id):
    if request.method == 'POST':
        # URL'den gelen id'ye göre ürünü bul ve MySQL'den sil (DELETE)
        urun = Urun.objects.get(id=urun_id)
        urun.delete()
    return redirect('dashboard')
def urun_guncelle(request, urun_id):
    # İlgili ürünü veritabanından getir
    urun = Urun.objects.get(id=urun_id)
    
    if request.method == 'POST':
        yeni_sayi = request.POST.get('urun_sayisi')
        if yeni_sayi:
            # Kolonu güncelle ve MySQL'e kaydet (UPDATE)
            urun.sayi = int(yeni_sayi)
            urun.save()
            return redirect('dashboard')
            
    return render(request, 'urun_guncelle.html', {'urun': urun})