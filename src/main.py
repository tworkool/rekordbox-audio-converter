from PySide6.QtWidgets import QApplication
from modules.gui1 import ConverterPromptWidget
import sys

if __name__ == "__main__":
    app = QApplication([])

    widget = ConverterPromptWidget()
    widget.resize(350, 250)
    widget.show()

    sys.exit(app.exec())
