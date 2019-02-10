import sys
from PySide2.QtWidgets import QApplication

from src.ui.views import MainWindow

if __name__ == '__main__':
    QApplication.setDesktopSettingsAware(False)
    app = QApplication(sys.argv)
    # Create a window, set its size, and give it a layout
    window = MainWindow()
    window.show()
    app.exec_()
