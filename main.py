"""
GxLauncher v2.0 - Game Launcher with Xbox Dark Theme
Main Entry Point
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from core.database import Database
from core.config import Config

def main():
    """Initialize and run the application"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("GxLauncher")
    app.setApplicationVersion("2.0.0")
    
    # Initialize core components
    db = Database()
    config = Config()
    
    # Create and show main window
    window = MainWindow(db, config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()