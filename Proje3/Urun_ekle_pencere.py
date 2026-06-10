# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Ekle import Ui_Dialog
from Proje3.db_manager import get_connection  # Veritabanı bağlantımız
from mysql.connector import Error

class UrunEklePencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)

        # Arayüz etiketlerini ayarlıyoruz
        self.ui.label.setText("Ürün Adı:")
        self.ui.label_2.setText("Ürün Sayısı:")
        self.ui.pushButton.setText("Ekle")

        # Buton bağlantısı
        self.ui.pushButton.clicked.connect(self.urun_ekle)

    def urun_ekle(self):
        ad = self.ui.lineEdit.text().strip().lower()
        sayi_str = self.ui.lineEdit_2.text().strip()

        if not ad or not sayi_str:
            self.ui.textEdit.setText("Ad ve sayı boş bırakılamaz.")
            return
        try:
            sayi = int(sayi_str)
        except ValueError:
            self.ui.textEdit.setText("Lütfen geçerli bir değer giriniz.")
            return
        if sayi <= 0:
            self.ui.textEdit.setText("Sayı sıfırdan büyük olmalı.")
            return

        db = get_connection()
        if not db:
            self.ui.textEdit.setText("Veritabanı bağlantısı başarısız!")
            return

        try:
            cursor = db.cursor(dictionary=True)
            
            # Ürün zaten var mı kontrolü
            cursor.execute("SELECT * FROM ogrenciler WHERE ad = %s", (ad,))
            if cursor.fetchone():
                self.ui.textEdit.setText("Ürün zaten var, Güncelle'yi kullanın.")
                return

            # MySQL INSERT Sorgusu
            sorgu = "INSERT INTO ogrenciler (ad, sayi) VALUES (%s, %s)"
            cursor.execute(sorgu, (ad, sayi))
            db.commit()
            self.ui.textEdit.setText(f"{ad} veritabanına başarıyla eklendi.")
        except Error as e:
            self.ui.textEdit.setText(f"Hata oluştu: {e}")
        finally:
            db.close()