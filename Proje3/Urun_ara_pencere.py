# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
from Proje3.Urun_ara import Ui_Dialog
from Proje3.db_manager import get_connection
from mysql.connector import Error

class UrunAraPencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_ara)

    def urun_ara(self):
        aranan = self.ui.lineEdit.text().strip().lower()
        
        db = get_connection()
        if not db:
            self.ui.textEdit.setText("Veritabanı bağlantısı başarısız!")
            return

        try:
            cursor = db.cursor(dictionary=True)
            # LIKE sorgusu ile arama yapıyoruz (boş bırakılırsa tümünü listeler)
            sorgu = "SELECT * FROM ogrenciler WHERE ad LIKE %s"
            cursor.execute(sorgu, (f"%{aranan}%",))
            sonuclar = cursor.fetchall()

            if not sonuclar:
                self.ui.textEdit.setText(f"{aranan} ile eşleşen bulunamadı.")
            else:
                metin = f"{'Ad':20}{'Sayı'}\n{'-'*30}\n"
                for k in sonuclar:
                    metin += f"{k['ad']:<20}{k['sayi']}\n"
                metin += f"{'-'*30}\nToplam {len(sonuclar)} ürün listelendi."
                self.ui.textEdit.setText(metin)
        except Error as e:
            self.ui.textEdit.setText(f"Hata: {e}")
        finally:
            db.close()