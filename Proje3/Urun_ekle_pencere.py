from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Ekle import Ui_Dialog
import Proje2.Modl4
import Proje2.Modl3

class UrunEklePencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)

        # Label yazıları
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

        urunler = Proje2.Modl4.Urunoku()
        for urun in urunler:
            if urun["ad"].lower() == ad:
                self.ui.textEdit.setText("Ürün zaten var, Güncelle'yi kullanın.")
                return

        urunler.append({"ad": ad, "sayi": sayi})
        Proje2.Modl3.UrunYaz(urunler)
        self.ui.textEdit.setText(f"{ad} envantere eklendi.")