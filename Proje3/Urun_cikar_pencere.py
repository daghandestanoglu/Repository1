# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Cıkar import Ui_Dialog
from Proje3.db_manager import get_connection
from mysql.connector import Error

class UrunCikarPencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_sil)

    def urun_sil(self):
        ad = self.ui.lineEdit.text().strip().lower()
        if not ad:
            self.ui.textEdit.setText("Ürün adı boş bırakılamaz.")
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

            # urunler tablosundan silme
            cursor.execute("DELETE FROM urunler WHERE ad = %s", (ad,))
            db.commit()
            self.ui.textEdit.setText(f"{ad} başarıyla veritabanından silindi.")
        except Error as e:
            self.ui.textEdit.setText(f"Hata: {e}")
        finally:
            db.close()