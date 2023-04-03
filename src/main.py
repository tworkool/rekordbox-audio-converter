from PySide6.QtWidgets import QApplication
from modules.gui1 import ConverterPromptWidget
#from modules.flac2wav import Flac2Wav
#from modules.gui.audioconvertermainwidget import AudioConverterMainWidget
import sys

if __name__ == "__main__":
    #converter = Flac2Wav()
    #converter.convert("D:/dev/python/qt-flac-converter-ui/test_data copy/Alignment", "D:/dev/python/qt-flac-converter-ui/test_data copy/Alignment/test")

    app = QApplication([])

    widget = ConverterPromptWidget()
    widget.resize(350, 250)
    widget.show()

    sys.exit(app.exec())
