from django.contrib import admin
from django.urls import path
from core.views import dashboard, urun_ekle, urun_sil, urun_guncelle # Yeni fonksiyonu çağır

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('ekle/', urun_ekle, name='urun_ekle'),
    path('sil/<int:urun_id>/', urun_sil, name='urun_sil'),
     path('guncelle/<int:urun_id>/', urun_guncelle, name='urun_guncelle'), # Dinamik silme adresi
]