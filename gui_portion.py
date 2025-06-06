import sys, requests, json
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSplashScreen, QDialog, QVBoxLayout, QTableWidget, QFileDialog, QTableWidgetItem, QHBoxLayout, QHeaderView, QGridLayout, QMainWindow)
from PySide6.QtGui import QCursor, QPixmap, QIcon
from PySide6.QtCore import Qt, QThread, Signal
from time import sleep

# -----------------------------------------------------------------

class Worker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url, method, data=None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data

    def run(self):
        try:
            if self.method == "GET":
                response = requests.get(self.url)
            # elif self.method == "POST":
            #     response = requests.post(self.url, json=self.data)
            else:
                self.error.emit(f"Unsupported method: {self.method}")
                return

            response.raise_for_status() # Raise an exception for HTTP errors
            self.finished.emit(response.text)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Request error: {e}")
        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")

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

class MainScreenWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainScreenWindow, self).__init__(parent)
        self.setWindowTitle("Music Player")
        self.musicCount = 10
        self.tableMusicDisplay = QTableWidget()
        self.tableMusicDisplay.setRowCount(self.musicCount)
        self.tableMusicDisplay.setColumnCount(3)
        self.tableMusicDisplay.setShowGrid(False)
        self.tableMusicDisplay.setHorizontalHeaderLabels(["Photo placeholder", "Music Name", "Duration"])

        for i in range(self.tableMusicDisplay.columnCount()):
            self.tableMusicDisplay.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            if i!=self.tableMusicDisplay.columnCount()-1:
                self.tableMusicDisplay.setEditTriggers(self.tableMusicDisplay.EditTrigger.NoEditTriggers)

        self.getDetails()

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutVertical = QVBoxLayout()
        widgetCentral.setLayout(layoutVertical)

        layoutVertical.addWidget(self.tableMusicDisplay)

        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")

        self.setWindowIcon(appIcon)

        # self.buttonUpload = QPushButton("Upload New Patient Data")
        # self.buttonUpload.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.buttonUpload.clicked.connect(self.uploadData)

    def getDetails(self):
        url = "http://127.0.0.1:8000/"
        self.worker = Worker(url, "GET")
        self.worker.finished.connect(self.populateTable)
        self.worker.error.connect(self.handleError)
        self.worker.start()

    def populateTable(self, detailsForTable):
        detailsForTable = json.loads(detailsForTable)
        # self.tableMusicDisplay.setRowCount(len(detailsForTable))
        for (i,musicDetails) in detailsForTable.items():
            self.tableMusicDisplay.setItem(int(i),1,QTableWidgetItem(musicDetails))
            self.tableMusicDisplay.setRowHeight(int(i), 60)
            if i==self.musicCount-1:
                break

    def handleError(self):
        pass

# -----------------------------------------------------------------

class AppWindows():
    def __init__(self):
        super(AppWindows, self).__init__()
        self.app = QApplication(sys.argv)
        self.windowSplashScreen = SplashScreenWindow()
        self.windowSplashScreen.delayForSometime(0.1)
        self.windowMainScreen = MainScreenWindow()
        self.windowMainScreen.show()
        self.windowSplashScreen.finish(self.windowMainScreen)
        del self.windowSplashScreen
        # self.app.setStyleSheet(Path("./Resources/styleSheet.qss").read_text())
        sys.exit(self.app.exec())

# -----------------------------------------------------------------

if __name__ == "__main__":
    AppWindows()