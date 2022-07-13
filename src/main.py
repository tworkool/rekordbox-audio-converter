from gui import ConverterPromptWidget
from PySide6 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = ConverterPromptWidget()
    widget.resize(500, 400)
    widget.show()

    sys.exit(app.exec())