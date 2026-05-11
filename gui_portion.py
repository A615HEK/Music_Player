import sys, requests, json
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSplashScreen, QDialog, QSlider, QVBoxLayout, QTableWidget, QFileDialog, QTableWidgetItem, QHBoxLayout, QHeaderView, QGridLayout, QMainWindow, QLineEdit, QToolTip, QSpacerItem)
from PySide6.QtGui import QPixmap, QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QPoint
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from time import sleep
from time_Calcer import Time_Values

# -----------------------------------------------------------------

# TODO:
# 1. Display list of available Playlists + New Playlist creation (within "Add to playlist" in "More Actions")
# 2. Storing Playlists
# 3. Click on playlists to view songs in it
# 4. Click on play (or) on a song to start playing it instead of the current song & queue
# 5. Add search bar

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

class MoreOptionsPopup(QWidget):
    def __init__(self, songName:str, parent=None):
        super(MoreOptionsPopup, self).__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.layoutVertical = QVBoxLayout()
        self.setLayout(self.layoutVertical)
        self.buttonMA_AddToPlaylist = QPushButton("Add To Playlist")
        self.buttonMA_AddToQueue = QPushButton("Add To Queue")
        # self.buttonMA_EditTags = QPushButton("Edit Tags")
        # self.buttonMA_AddToFav = QPushButton("Add To Favourites")
        self.layoutVertical.addWidget(self.buttonMA_AddToPlaylist)
        self.layoutVertical.addWidget(self.buttonMA_AddToQueue)
        self.buttonMA_AddToPlaylist.clicked.connect(lambda: self.AddToPlaylist(songName, "Default_Playlist"))
        self.buttonMA_AddToQueue.clicked.connect(lambda: self.AddToPlaylist(songName))

    def AddToPlaylist(self, songName:str, playlistName:str = "Queue"):
        print(f"Add to {playlistName} -> {songName}")
        self.close()

    def displayPopup(self, parentPos:QPoint):
        self.move(parentPos)
        self.show()

# -----------------------------------------------------------------

class MainScreenWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainScreenWindow, self).__init__(parent)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Music Player")
        self.currentlyPlaying = 0
        self.musicCount = 10
        self.windowOnline = None
        self.windowPlaylists = None
        self.tableMusicDisplay = QTableWidget()
        self.tableMusicDisplay.setRowCount(self.musicCount)
        self.tableMusicDisplay.setColumnCount(4)
        self.tableMusicDisplay.setShowGrid(False)
        self.tableMusicDisplay.setHorizontalHeaderLabels(["Photo placeholder", "Music Name", "Duration", "More Actions"]) # Only for debug

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

        self.buttonPlay = QPushButton("Play")
        self.buttonPlay.setCheckable(True)
        self.buttonPlay.clicked.connect(self.buttonPlayPause)

        self.sliderTime = QSlider()
        self.sliderTime.setOrientation(Qt.Horizontal)
        self.sliderTime.sliderMoved.connect(lambda: self.sliderTimerChanged("SliderMoved"))
        self.sliderTime.sliderPressed.connect(lambda: self.sliderTimerChanged("SliderPressed"))
        self.sliderTime.sliderReleased.connect(lambda: self.sliderTimerChanged("SliderReleased"))
        self.sliderTime.valueChanged.connect(self.sliderTooltipUpdate)
        self.sliderTooltipUpdate()
        self.mediaPlayer.positionChanged.connect(self.sliderTimerUpdate)
        self.mediaPlayer.mediaStatusChanged.connect(self.playNextMusic)

        self.menuHome = self.menuBar().addMenu("Home")
        self.menuYoutube = self.menuBar().addMenu("Youtube")
        self.menuSearchBar = self.menuBar().addMenu("Search")

        actionGoHome = self.menuHome.addAction("Go to Home")
        actionGoPlaylists = self.menuHome.addAction("View Playlists")
        actionGoOnline = self.menuYoutube.addAction("Search Online")

        actionGoHome.triggered.connect(lambda: self.triggeredByAction(actionGoHome.text().lower()))
        actionGoPlaylists.triggered.connect(lambda: self.triggeredByAction(actionGoPlaylists.text().lower()))
        actionGoOnline.triggered.connect(lambda: self.triggeredByAction(actionGoOnline.text().lower()))

        layoutPlayer.addWidget(QLabel()) # Name of the song/music
        layoutPlayer.addStretch()
        layoutPlayer.addWidget(QLabel()) # Current timestamp
        layoutPlayer.addWidget(self.sliderTime) # Slider
        layoutPlayer.addWidget(QLabel()) # Duration of the song/music
        layoutPlayer.addWidget(self.buttonPlay) # Play/Pause button
        layoutVertical.addWidget(self.widgetPlayer)

    def triggeredByAction(self, triggeringActionText:str):
        if "online" in triggeringActionText:
            print("Search Online")
            self.showOnlineWindow()
        elif "playlist" in triggeringActionText:
            print("Viewing Playlists")
            self.showPlaylistsWindow()
        else:
            pass

    def showPlaylistsWindow(self):
        if not self.windowPlaylists:
            self.windowPlaylists = PlaylistsWindow(self)
        self.hide()
        self.windowPlaylists.show()

    def showOnlineWindow(self):
        if not self.windowOnline:
            self.windowOnline = YoutubeWindow(self)
        self.hide()
        self.windowOnline.show()

    def populateTable(self, detailsForTable):
        self.detailsForTable = json.loads(detailsForTable)
        self.musicCount = len(self.detailsForTable)
        self.tableMusicDisplay.setRowCount(self.musicCount) # Dynamically update based on table size
        for (i,musicDetails) in self.detailsForTable.items():
            buttonMoreActions = QPushButton("...")
            buttonMoreActions.setProperty("row_idx", i)
            buttonMoreActions.clicked.connect(self.moreActionsClicked)
            self.tableMusicDisplay.setItem(int(i), 1, QTableWidgetItem(musicDetails["filename"]))
            self.tableMusicDisplay.setItem(int(i), 2, QTableWidgetItem(musicDetails["duration"]))
            self.tableMusicDisplay.setCellWidget(int(i), 3, buttonMoreActions)
            self.tableMusicDisplay.setRowHeight(int(i), 60)
            if i==self.musicCount-1:
                break
        self.selectedAudio(0, 1)
        self.buttonPlay.click()

    def moreActionsClicked(self):
        clicked_RowID = self.sender().property("row_idx")
        songName = self.detailsForTable[clicked_RowID]["filename"]
        MA_Popup = MoreOptionsPopup(songName)
        MA_Pos = self.sender().mapToGlobal(QPoint(0, self.sender().height()))
        MA_Popup.displayPopup(MA_Pos)

    def selectedAudio(self, row, column):
        self.buttonPlay.setChecked(False)
        self.selectedAudioID = row
        if column != 3:
            self.mediaPlayer.setSource(QUrl().fromLocalFile(self.detailsForTable[str(row)]["path"]))
            self.currentlyPlaying = row
            self.buttonPlay.click()
        time_vals = list(map(int, map(str.strip, self.detailsForTable[str(row)]["duration"].split(":"))))
        audio_time_in_secs = 0
        if len(time_vals)>3:
            audio_time_in_secs += time_vals[0]*86400
        audio_time_in_secs += sum(val*(60**(len(time_vals)-1-idx)) for idx, val in enumerate(time_vals[-3:]))
        self.sliderTime.setRange(0, audio_time_in_secs*1000)
        self.widgetPlayer.layout().itemAt(0).widget().setText(self.detailsForTable[str(row)]["filename"])
        self.widgetPlayer.layout().itemAt(2).widget().setText("0 : 00")
        self.widgetPlayer.layout().itemAt(4).widget().setText(self.detailsForTable[str(row)]["duration"])

    def buttonPlayPause(self):
        if self.buttonPlay.isChecked():
            self.mediaPlayer.play()
            self.buttonPlay.setText("Pause")
        else:
            self.mediaPlayer.pause()
            self.buttonPlay.setText("Play")

    def sliderTimerChanged(self, signalType:str):
        if signalType == "SliderReleased" and self.buttonPlay.isChecked():
            # Play on release only if it was initially playing
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.pause()
        # Update the song to the timestamp specified by the slider's new position
        self.mediaPlayer.setPosition(self.sliderTime.value())
        # Updates tooltip dynamically
        currentTime = Time_Values((self.sliderTime.value()/1000).__floor__()).__repr__()
        self.sliderTime.setToolTip(currentTime)
        cursorPos = self.cursor().pos()
        QToolTip.showText(cursorPos, currentTime, self.sliderTime)

    def sliderTimerUpdate(self):
        self.widgetPlayer.layout().itemAt(2).widget().setText(Time_Values((self.sliderTime.value()/1000).__floor__()).__repr__())
        self.sliderTime.setValue(self.mediaPlayer.position())

    def sliderTooltipUpdate(self):
        self.sliderTime.setToolTip(Time_Values((self.sliderTime.value()/1000).__floor__()).__repr__())

    def playNextMusic(self):
        if self.mediaPlayer.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.currentlyPlaying < self.musicCount-1: # Not the last song
                self.selectedAudio(self.currentlyPlaying+1, 1)
            else: # If the song that finished playing was the last song
                self.selectedAudio(0, 1)
                self.buttonPlay.click()

    def handleError(self):
        print("There's been an error mate...")

# -----------------------------------------------------------------

class PlaylistsWindow(QMainWindow):
    def __init__(self, mainWindow:QMainWindow | MainScreenWindow, parent=None):
        super(PlaylistsWindow, self).__init__(parent)
        self.setGeometry(200, 200, 400, 200)
        self.setWindowTitle("Music Player")
        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")
        self.setWindowIcon(appIcon)

        self.windowHome = mainWindow

        self.menuHome = self.menuBar().addMenu("Home")
        self.menuYoutube = self.menuBar().addMenu("Youtube")
        actionGoHome = self.menuHome.addAction("Go to Home")
        actionGoPlaylists = self.menuHome.addAction("View Playlists")
        actionGoOnline = self.menuYoutube.addAction("Search Online")
        actionGoHome.triggered.connect(lambda: self.triggeredByAction(actionGoHome.text().lower()))
        actionGoPlaylists.triggered.connect(lambda: self.triggeredByAction(actionGoPlaylists.text().lower()))
        actionGoOnline.triggered.connect(lambda: self.triggeredByAction(actionGoOnline.text().lower()))

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutHorizontal = QHBoxLayout()
        widgetCentral.setLayout(layoutHorizontal)
        self.buttonSearch = QPushButton("Default Playlist 1")
        layoutHorizontal.addWidget(self.buttonSearch)

    def triggeredByAction(self, triggeringActionText:str):
        if "home" in triggeringActionText:
            print("Go to Home")
            self.hide()
            if self.windowHome:
                self.windowHome.show()
                self.destroy()
        elif "online" in triggeringActionText:
            print("Search Online")
            self.hide()
            self.windowHome.showOnlineWindow()
            self.destroy()
        else:
            pass

# -----------------------------------------------------------------

class YoutubeWindow(QMainWindow):
    def __init__(self, mainWindow:QMainWindow | MainScreenWindow, parent=None):
        super(YoutubeWindow, self).__init__(parent)
        self.setGeometry(200, 200, 400, 200)
        self.setWindowTitle("Music Player")
        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")
        self.setWindowIcon(appIcon)

        self.windowHome = mainWindow

        self.menuHome = self.menuBar().addMenu("Home")
        self.menuYoutube = self.menuBar().addMenu("Youtube")
        actionGoHome = self.menuHome.addAction("Go to Home")
        actionGoPlaylists = self.menuHome.addAction("View Playlists")
        actionGoOnline = self.menuYoutube.addAction("Search Online")
        actionGoHome.triggered.connect(lambda: self.triggeredByAction(actionGoHome.text().lower()))
        actionGoPlaylists.triggered.connect(lambda: self.triggeredByAction(actionGoPlaylists.text().lower()))
        actionGoOnline.triggered.connect(lambda: self.triggeredByAction(actionGoOnline.text().lower()))

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutHorizontal = QHBoxLayout()
        widgetCentral.setLayout(layoutHorizontal)
        self.lineEditSearch = QLineEdit("")
        self.lineEditSearch.setPlaceholderText("Search YouTube...")
        self.buttonSearch = QPushButton("Search")
        self.buttonSearch.clicked.connect(self.searchSong)
        layoutHorizontal.addWidget(self.lineEditSearch)
        layoutHorizontal.addWidget(self.buttonSearch)

    def searchSong(self):
        # TODO:
        # 1. Search clicked -> Disable LineEdit till search reults are back
        print(self.lineEditSearch.text())

    def triggeredByAction(self, triggeringActionText:str):
        if "home" in triggeringActionText:
            print("Go to Home")
            self.hide()
            if self.windowHome:
                self.windowHome.show()
                self.destroy()
        elif "playlist" in triggeringActionText:
            print("Viewing Playlists")
            self.hide()
            self.windowHome.showPlaylistsWindow()
            self.destroy()
        else:
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
        self.worker.start()
        self.worker.finished.connect(self.windowMainScreen.populateTable)
        self.worker.error.connect(self.windowMainScreen.handleError)

# -----------------------------------------------------------------

if __name__ == "__main__":
    AppWindows()