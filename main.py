#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import TTSDatasetCreator

if __name__ == "__main__":
    # Fix for high DPI screens
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    window = TTSDatasetCreator()
    window.show()
    sys.exit(app.exec())