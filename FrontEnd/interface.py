import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import *


camninho_icone = r"C:\\TradutorDeCodigo\\assets\\icon.png"

# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeCast")
        self.setWindowIcon(QIcon(camninho_icone))
        self.setGeometry(200, 200, 480, 320)
        self.Inferface()


    def Inferface(self):
        texto1 = QLabel('Login: ', self)
        texto1.move(40,50)

        botao1 = QPushButton('SAIR', self)
        botao1.move(100, 200)
        botao1.clicked.connect(self.sair)

        self.caixa_texto1 = QLineEdit(self)
        self.caixa_texto1.setPlaceholderText('Digite seu nome de usuário')
        self.caixa_texto1.move(90, 48)

        texto2 = QLabel('Senha: ', self)
        texto2.move(40, 74)

        self.caixa_texto2 = QLineEdit(self)
        self.caixa_texto2.setPlaceholderText('Digite sua senha')
        self.caixa_texto2.setEchoMode(QLineEdit.EchoMode.Password)
        self.caixa_texto2.move(90, 72)

        self.show()

    def sair(self):
        sys.exit(qt.exec())


qt = QApplication(sys.argv)
app = MainWindow()
sys.exit(qt.exec())
