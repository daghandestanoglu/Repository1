from django.shortcuts import render
from .models import Urun

def dashboard(request):
    urunler = Urun.objects.all()
    toplam_urun_sayisi = urunler.count()
    
    context = {
        'toplam_urun': toplam_urun_sayisi,
        'urunler': urunler,  # Tüm ürün listesini şablona fırlatıyoruz
    }
    return render(request, 'dashboard.html', context)