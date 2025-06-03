import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSplashScreen, QDialog, QLineEdit, QVBoxLayout, QTableWidget, QFileDialog, QTableWidgetItem, QHBoxLayout, QHeaderView, QGridLayout, QSizePolicy, QButtonGroup, QSlider, QComboBox)
from PySide6.QtGui import QCursor, QPixmap, QImage
from PySide6.QtCore import Qt
from time import sleep

# -----------------------------------------------------------------

class SplashScreenWindow(QSplashScreen):
    def __init__(self):
        super(SplashScreenWindow, self).__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.pixmapLogo = QPixmap("./Resources/Splash_Screen_Logo.png")
        self.setPixmap(self.pixmapLogo)

    def delayForSometime(self, sleepTime=0.001):
        opaqueness = 0
        self.setWindowOpacity(opaqueness)
        self.show()
        while opaqueness < 1:
            sleep(sleepTime)
            self.setWindowOpacity(opaqueness)
            opaqueness+=0.08
        sleep(1)
        self.close()

    def __del__(self):
        print("Destroying Splash Screen Window")

# -----------------------------------------------------------------

class AppWindows():
    def __init__(self):
        super(AppWindows, self).__init__()
        self.app = QApplication(sys.argv)
        self.windowSplashScreen = SplashScreenWindow()
        # self.nextWindow maari inga varanum
        self.windowSplashScreen.delayForSometime(0.1)
        # Show next window
        # self.windowSplashScreen.finish(self.windowLogin)
        del self.windowSplashScreen
        # self.windowLogin.buttonLogin.clicked.connect(self.openMainWindow)
        # self.app.setStyleSheet(Path("./Resources/styleSheet.qss").read_text())
        sys.exit(self.app.exec())

# -----------------------------------------------------------------

def main() -> None:
    """
    Use this function to run individual windows for debugging/layout setting
    """
    app = QApplication(sys.argv)
    print(sys.argv)
    splashScreenWindow = SplashScreenWindow()
    splashScreenWindow.showMessage("Loading the app...")
    # loginWindow = LoginWindow()
    # loginWindow.show()
    # mainScreenWindow = MainScreenWindow()
    # mainScreenWindow.show()
    # -------------------------------
    # dicomWindow = DicomWindow()
    # splashScreenWindow.delayForSometime(0.1)
    # dicomWindow.show()
    # splashScreenWindow.finish(dicomWindow)
    # del splashScreenWindow
    # app.setStyleSheet(Path("./Resources/styleSheet.qss").read_text())
    # -------------------------------
    # Starting the event loop
    sys.exit(app.exec())

# -----------------------------------------------------------------

if __name__ == "__main__":
    AppWindows()