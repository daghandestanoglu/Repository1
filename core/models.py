from django.db import models

class Urun(models.Model):
    ad = models.CharField(max_length=255)
    sayi = models.IntegerField()

    class Meta:
        db_table = 'urunler'  # Django'nun sıfırdan tablo açmasını engeller, mevcut 'urunler' tablonu bağlar.
        managed = False       # Mevcut tabloya Django'nun müdahale etmesini (silme/değiştirme) önler.

    def __str__(self):
        return self.ad