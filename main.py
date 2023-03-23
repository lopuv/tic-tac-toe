import sys
import Window
from PyQt6.QtWidgets import *

App = QApplication(sys.argv)

window = Window.Window()

sys.exit(App.exec())
