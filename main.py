#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import TTSDatasetCreator
from PyQt6.QtGui import QIcon

if __name__ == "__main__":
    # Fix for high DPI screens
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "app_icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = TTSDatasetCreator()
    window.show()
    sys.exit(app.exec())