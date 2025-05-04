import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CodeCast")
        

        texto1 = QLabel('Bem-vindo', self)
        texto1.move(100, 50)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
