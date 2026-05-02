from PyQt6.QtWidgets import QDialog
from Proje3.Urun_ara import Ui_Dialog
import Proje2.Modl4

class UrunAraPencere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setReadOnly(True)
        self.ui.pushButton.clicked.connect(self.urun_ara)

    def urun_ara(self):
        aranan = self.ui.lineEdit.text().strip().lower()
        urunler = Proje2.Modl4.Urunoku()

        if not urunler:
            self.ui.textEdit.setText("Envanter boş.")
            return

        sonuclar = [k for k in urunler if aranan in k["ad"].lower()]

        if not sonuclar:
            self.ui.textEdit.setText(f"{aranan} ile eşleşen bulunamadı.")
        else:
            metin = f"{'Ad':20}{'Sayı'}\n{'-'*30}\n"
            for k in sonuclar:
                metin += f"{k['ad']:<20}{k['sayi']}\n"
            metin += f"{'-'*30}\nToplam {len(sonuclar)} ürün."
            self.ui.textEdit.setText(metin)