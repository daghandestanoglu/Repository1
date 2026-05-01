from PyQt6.QtWidgets import QDialog
from Proje3.Urun_Cıkar import Ui_Dialog
import Proje2.Modl4
import Proje2.Modl3

class UrunCikarPencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_sil)

    def urun_sil(self):
        ad = self.ui.lineEdit.text().strip()
        if not ad:
            self.ui.textEdit.setText("Ürün adı boş bırakılamaz.")
            return

        urunler = Proje2.Modl4.Urunoku()
        yeni_liste = [k for k in urunler if k["ad"].lower() != ad.lower()]

        if len(yeni_liste) == len(urunler):
            self.ui.textEdit.setText(f"{ad} bulunamadı.")
        else:
            Proje2.Modl3.UrunYaz(yeni_liste)
            self.ui.textEdit.setText(f"{ad} başarıyla silindi.")