import sys
from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from logic import LoginLogic

app = QApplication(sys.argv)
ui_file = Path(__file__).with_name("login.ui")
window = uic.loadUi(str(ui_file))
logic = LoginLogic(window)
window.show()
sys.exit(app.exec_())
