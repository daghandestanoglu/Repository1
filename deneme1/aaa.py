from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

app = QApplication([])
pencere = uic.loadUi("deneme1/untitled.ui")

def verileri_al():
    # 1. kutudaki metni oku
    metin1 = ikinci_pencere.textEdit.toPlainText()
    # 2. kutudaki metni oku
    metin2 = ikinci_pencere.textEdit_2.toPlainText()
    
    print(f"Kullanıcı: {metin1}")

    # DİKKAT: Şifreyi tırnak içine aldık "123" çünkü textEdit metin döndürür
    if metin2 != "123":
        print("Yanlış şifre!")
        return False
    else:
        print("Şifre doğru, Ayar penceresi açılıyor...")
        ayar_penceresini_ac() # Şifre doğruysa bu fonksiyonu çağırıyoruz
        return True

def ayar_penceresini_ac():
    global ayar_pencere
    ayar_pencere = uic.loadUi("deneme1/Ayar.ui")
    ayar_pencere.show()
    # Opsiyonel: Giriş penceresini kapatmak istersen:
    # ikinci_pencere.close()

def tiklandi():
    global ikinci_pencere 
    ikinci_pencere = uic.loadUi("deneme1/Giris.ui")
    ikinci_pencere.show()
    ikinci_pencere.pushButton.clicked.connect(verileri_al)

pencere.pushButton.clicked.connect(tiklandi)

pencere.show()
app.exec_()
