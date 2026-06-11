# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Guncelle import Ui_Dialog
from Proje3.db_manager import get_connection
from mysql.connector import Error

class UrunGuncellePencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_guncelle)

    def urun_guncelle(self):
        ad = self.ui.lineEdit.text().strip().lower()
        sayi_str = self.ui.lineEdit_2.text().strip()

        if not ad or not sayi_str:
            self.ui.textEdit.setText("Ad ve sayı boş bırakılamaz.")
            return
        try:
            yeni_sayi = int(sayi_str)
        except ValueError:
            self.ui.textEdit.setText("Lütfen geçerli bir değer giriniz.")
            return
        if yeni_sayi <= 0:
            self.ui.textEdit.setText("Sayı sıfırdan büyük olmalı.")
            return

        db = get_connection()
        if not db:
            self.ui.textEdit.setText("Veritabanı bağlantısı başarısız!")
            return

        try:
            cursor = db.cursor()
            # urunler tablosunda kontrol
            cursor.execute("SELECT * FROM urunler WHERE ad = %s", (ad,))
            if not cursor.fetchone():
                self.ui.textEdit.setText(f"{ad} bulunamadı.")
                return

            # urunler tablosunda güncelleme
            cursor.execute("UPDATE urunler SET sayi = %s WHERE ad = %s", (yeni_sayi, ad))
            db.commit()
            self.ui.textEdit.setText(f"{ad} miktarı {yeni_sayi} olarak güncellendi.")
        except Error as e:
            self.ui.textEdit.setText(f"Hata: {e}")
        finally:
            db.close()