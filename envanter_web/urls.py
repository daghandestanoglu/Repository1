from django.contrib import admin
from django.urls import path
from core.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),  # Hata buradaydı; get_urls() değil, sadece .urls olacak
    path('', dashboard, name='dashboard'),
]