import sys, requests, json
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSplashScreen, QDialog, QSlider, QVBoxLayout, QTableWidget, QFileDialog, QTableWidgetItem, QHBoxLayout, QHeaderView, QGridLayout, QMainWindow)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
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
        # self.getDetails()
        self.setWindowTitle("Music Player")
        self.musicCount = 10
        self.tableMusicDisplay = QTableWidget()
        self.tableMusicDisplay.setRowCount(self.musicCount)
        self.tableMusicDisplay.setColumnCount(4)
        self.tableMusicDisplay.setShowGrid(False)
        self.tableMusicDisplay.setHorizontalHeaderLabels(["Photo placeholder", "Music Name", "Duration", "More Actions"])

        for i in range(self.tableMusicDisplay.columnCount()):
            self.tableMusicDisplay.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            if i!=self.tableMusicDisplay.columnCount()-1:
                self.tableMusicDisplay.setEditTriggers(self.tableMusicDisplay.EditTrigger.NoEditTriggers)

        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutVertical = QVBoxLayout()
        widgetCentral.setLayout(layoutVertical)
        layoutVertical.addWidget(self.tableMusicDisplay)

        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")
        self.setWindowIcon(appIcon)

        self.tableMusicDisplay.cellClicked.connect(self.selectedAudio)

        self.widgetPlayer = QWidget()
        layoutPlayer = QHBoxLayout()
        self.widgetPlayer.setLayout(layoutPlayer)

        self.buttonPlay = QPushButton("Play/Pause")
        self.buttonPlay.setCheckable(True)
        self.buttonPlay.clicked.connect(self.buttonPlayPause)

        self.sliderTime = QSlider()
        self.sliderTime.setOrientation(Qt.Horizontal)
        self.sliderTime.sliderReleased.connect(self.sliderTimerReleased)
        self.sliderTime.sliderMoved.connect(self.sliderTimerMoved)

        layoutPlayer.addWidget(QLabel())
        layoutPlayer.addWidget(QLabel())
        layoutPlayer.addWidget(self.sliderTime)
        layoutPlayer.addWidget(self.buttonPlay)
        layoutVertical.addWidget(self.widgetPlayer)

    def populateTable(self, detailsForTable):
        self.detailsForTable = json.loads(detailsForTable)
        for (i,musicDetails) in self.detailsForTable.items():
            self.tableMusicDisplay.setItem(int(i), 1, QTableWidgetItem(musicDetails["filename"]))
            self.tableMusicDisplay.setItem(int(i), 2, QTableWidgetItem(musicDetails["duration"]))
            self.tableMusicDisplay.setRowHeight(int(i), 60)
            if i==self.musicCount-1:
                break

    def selectedAudio(self, row, column):
        self.buttonPlay.setChecked(False)
        self.selectedAudioID = row
        if column != 3:
            self.mediaPlayer.setSource(QUrl().fromLocalFile(self.detailsForTable[str(row)]["path"]))
            self.buttonPlay.click()
        time_vals = list(map(int, map(str.strip, self.detailsForTable[str(row)]["duration"].split(":"))))
        audio_time_in_secs = 0
        if len(time_vals)>3:
            audio_time_in_secs += time_vals[0]*86400
        audio_time_in_secs += sum(val*(60**(len(time_vals)-1-idx)) for idx, val in enumerate(time_vals[-3:]))
        self.sliderTime.setRange(0, audio_time_in_secs)
        self.widgetPlayer.layout().itemAt(0).widget().setText(self.detailsForTable[str(row)]["filename"])
        self.widgetPlayer.layout().itemAt(1).widget().setText(self.detailsForTable[str(row)]["duration"])

    def buttonPlayPause(self):
        if self.buttonPlay.isChecked():
            print("Play")
            self.mediaPlayer.play()
        else:
            print("Pause")
            self.mediaPlayer.pause()

    def sliderTimerMoved(self):
        print("Moved:", self.sliderTime.value())

    def sliderTimerReleased(self):
        print("Released:", self.sliderTime.value())

    def handleError(self):
        pass

# -----------------------------------------------------------------

class AppWindows():
    def __init__(self):
        super(AppWindows, self).__init__()
        self.app = QApplication(sys.argv)
        self.windowSplashScreen = SplashScreenWindow()
        self.windowMainScreen = MainScreenWindow()
        self.getDetails()
        self.windowSplashScreen.delayForSometime(0.1)
        self.windowMainScreen.show()
        self.windowSplashScreen.finish(self.windowMainScreen)
        del self.windowSplashScreen
        # self.app.setStyleSheet(Path("./Resources/styleSheet.qss").read_text())
        sys.exit(self.app.exec())

    def getDetails(self):
        url = "http://127.0.0.1:8000/"
        self.worker = Worker(url, "GET")
        self.worker.finished.connect(self.windowMainScreen.populateTable)
        self.worker.error.connect(self.windowMainScreen.handleError)
        self.worker.start()

# -----------------------------------------------------------------

if __name__ == "__main__":
    AppWindows()