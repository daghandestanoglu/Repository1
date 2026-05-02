from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Guncelle import Ui_Dialog
import Proje2.Modl4
import Proje2.Modl3

class UrunGuncellePencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_guncelle)

    def urun_guncelle(self):
        ad = self.ui.lineEdit.text().strip()
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

        urunler = Proje2.Modl4.Urunoku()
        guncel = False
        for urun in urunler:
            if urun["ad"].lower() == ad.lower():
                urun["sayi"] = yeni_sayi
                guncel = True
                break

        if guncel:
            Proje2.Modl3.UrunYaz(urunler)
            self.ui.textEdit.setText(f"{ad} sayısı {yeni_sayi} olarak güncellendi.")
        else:
            self.ui.textEdit.setText(f"{ad} bulunamadı.")