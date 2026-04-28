import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton,QTextEdit,QVBoxLayout
from PyQt6.QtGui import QIcon

class MyApp(QWidget):
    def __init__ (self):
        super().__init__()
        self.setWindowTitle('Hello app')
        #self.setWindowIcon(QIcon('maps.ico'))
        self.resize(500,350)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.inputField = QLineEdit()
        self.button = QPushButton('&Say Hello',clicked=self.sayHello)
        #button.clicked.connect(self.sayHello)
        self.output = QTextEdit()

        layout.addWidget(self.inputField)
        layout.addWidget(self.button)
        layout.addWidget(self.output) 

    def sayHello(self):
        inputText = self.inputField.text()
        self.output.setText("Hello {0}".format(inputText))


#app = QApplication([])
app = QApplication(sys.argv)
app.setStyle('''
    QWİdget {
        font-size: 25px;
    }
    QPushButton {
        font-size: 20px;
    }
             ''')

window = MyApp()
window.show()

app.exec()