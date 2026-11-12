import sys, requests, json
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSplashScreen, QDialog, QSlider, QVBoxLayout, QTableWidget, QFileDialog, QTableWidgetItem, QHBoxLayout, QHeaderView, QGridLayout, QMainWindow, QLineEdit, QToolTip, QSpacerItem)
from PySide6.QtGui import QPixmap, QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QPoint
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from time import sleep
from time_Calcer import Time_Values
from backend_logic import scan_and_return_songlist, youtube_search_logic, edit_playlist, list_playlists

# -----------------------------------------------------------------
# * -> Meaning Priority
# TODO:
# 1. Click on playlists to view songs in it
# * Ability to view queue and add songs to queue
# NICE_TO_HAVES:
# 1. Mini player interface
# 2. Have Audio Visualiser
# 3. Skin customizability

# -----------------------------------------------------------------

def commonSearchBarAssets(placeHolderText:str, searchLogic, searchBarVisibility:bool = False) -> tuple[QHBoxLayout, bool]:
    # TODO:
    # 1. Replace searchButton's text with Search image
    search_HorizontalLayout = QHBoxLayout()
    searchBar = QLineEdit()
    searchBar.setPlaceholderText(placeHolderText)
    searchBar.setClearButtonEnabled(True)
    searchBar.setVisible(searchBarVisibility)
    searchBar.returnPressed.connect(searchLogic)
    searchButton = QPushButton("Search")
    searchButton.clicked.connect(searchLogic)

    search_HorizontalLayout.addWidget(searchBar)
    search_HorizontalLayout.addWidget(searchButton)

    return search_HorizontalLayout, searchBarVisibility

def commonMenubarAssets(self:QMainWindow):
    self.menuHome = self.menuBar().addMenu("Home")
    self.menuYoutube = self.menuBar().addMenu("Youtube")
    self.menuOptions = self.menuBar().addMenu("Options")
    self.toggleText = "On"

    self.actionGoHome = self.menuHome.addAction("Go to Home")
    self.actionGoPlaylists = self.menuHome.addAction("View Playlists")
    self.actionGoOnline = self.menuYoutube.addAction("Search Online")
    self.actionToggleOnTop = self.menuOptions.addAction(f"Toggle Anchor - {self.toggleText}")

    self.actionGoHome.triggered.connect(lambda: triggeredByAction(self, self.actionGoHome.text().lower()))
    self.actionGoPlaylists.triggered.connect(lambda: triggeredByAction(self, self.actionGoPlaylists.text().lower()))
    self.actionGoOnline.triggered.connect(lambda: triggeredByAction(self, self.actionGoOnline.text().lower()))
    self.actionToggleOnTop.triggered.connect(lambda: windowOnTopFlagToggler(self))

def windowOnTopFlagToggler(self:QMainWindow):
    import ctypes
    import ctypes.wintypes
    self.windowOnTopFlag = not self.windowOnTopFlag
    self.toggleText = "On" if self.windowOnTopFlag else "Off"
    self.actionToggleOnTop.setText(f"Toggle Anchor - {self.toggleText}")
    hwnd = int(self.winId())
    hwnd_insert = ctypes.wintypes.HWND(-1 if self.windowOnTopFlag else -2)
    ctypes.windll.user32.SetWindowPos(hwnd, hwnd_insert, 0, 0, 0, 0, 3)

def triggeredByAction(self:QMainWindow, triggeringActionText:str):
    if "home" in triggeringActionText:
        # Check if calling window is home -> True: Ignore and Return, False: Continue fn
        if self.windowName == "MainScreenWindow":
            return
        if self.windowHome:
            print("Go to Home")
            self.hide()
            self.windowHome.show()
            self.destroy()
    elif "playlist" in triggeringActionText:
        # Check if calling window is playlist -> True: Ignore and Return, False: Continue fn
        if self.windowName == "PlaylistWindow":
            return
        print("Viewing Playlists")
        if self.windowName == "MainScreenWindow":
            self.showPlaylistsWindow()
        else:
            self.hide()
            self.windowHome.showPlaylistsWindow()
            self.destroy()
    elif "online" in triggeringActionText:
        # Check if calling window is youtube -> True: Ignore and Return, False: Continue fn
        if self.windowName == "YoutubeWindow":
            return
        print("Search Online")
        if self.windowName == "MainScreenWindow":
            self.showOnlineWindow()
        else:
            self.hide()
            self.windowHome.showOnlineWindow()
            self.destroy()
    else:
        pass

# -----------------------------------------------------------------

# class Worker(QThread):
#     finished = Signal(str)
#     error = Signal(str)

#     def __init__(self, method:str, data=None):
#         super().__init__()
#         # self.url = url
#         # self.method = method
#         self.data = data
#         self.method = method

#     def run(self):
#         try:
#             # if self.method == "GET":
#             #     response = requests.get(self.url)
#             # elif self.method == "POST":
#             #     response = requests.post(self.url, json=self.data)
#             if self.method == "get_song_list":
#                 response = scan_and_return_songlist()
#                 self.finished.emit(response)
#             else:
#                 self.error.emit(f"Unsupported method: {self.method}")
#             # response.raise_for_status() # Raise an exception for HTTP errors
#         except Exception as e:
#             self.error.emit(f"An unexpected error occurred: {e}")

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
    def __init__(self, songDetails:dict, parent=None):
        super(MoreOptionsPopup, self).__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.layoutVertical = QVBoxLayout()
        self.setLayout(self.layoutVertical)
        self.buttonMA_AddToPlaylist = QPushButton("Add To Playlist")
        self.buttonMA_NewPlaylist = QPushButton("New Playlist")
        self.buttonMA_AddToQueue = QPushButton("Add To Queue")

        songName = songDetails["fileName"]

        self.layoutHorizontal_NewPlaylist = QHBoxLayout()
        self.lineEditMA_PlaylistName = QLineEdit(placeholderText="Playlist Name...")
        self.buttonMA_Done = QPushButton("Done")
        self.layoutVertical.addWidget(self.lineEditMA_PlaylistName)
        self.layoutVertical.addWidget(self.buttonMA_Done)

        # self.buttonMA_EditTags = QPushButton("Edit Tags")
        # self.buttonMA_AddToFav = QPushButton("Add To Favourites")
        self.layoutVertical.addWidget(self.buttonMA_AddToPlaylist)
        self.layoutVertical.addWidget(self.buttonMA_NewPlaylist)
        self.layoutVertical.addLayout(self.layoutHorizontal_NewPlaylist)
        self.layoutVertical.addWidget(self.buttonMA_AddToQueue)
        self.buttonMA_AddToPlaylist.clicked.connect(lambda: self.AddToPlaylist(songName, "Default_Playlist"))
        self.buttonMA_AddToQueue.clicked.connect(lambda: self.AddToPlaylist(songName))
        
        self.buttonMA_NewPlaylist.clicked.connect(self.showNewPlaylist)
        self.buttonMA_Done.clicked.connect(lambda: self.createNewPlaylist(songDetails))

        self.lineEditMA_PlaylistName.hide()
        self.buttonMA_Done.hide()
        self.buttonMA_Done.setChecked(False)

    def createNewPlaylist(self, songDetails:dict):
        edit_playlist(self.lineEditMA_PlaylistName.text(), "ADD_SONGS", songDetails)
        self.lineEditMA_PlaylistName.hide()
        self.buttonMA_Done.hide()
        self.buttonMA_Done.setChecked(False)
        self.close()

    def showNewPlaylist(self):
        self.lineEditMA_PlaylistName.show()
        self.buttonMA_Done.show()
        self.lineEditMA_PlaylistName.setFocus()
        self.buttonMA_Done.setChecked(False)

    def AddToPlaylist(self, songName:str, playlistName:str = "Queue"):
        # TODO:
        # 1. Display list of existing playlists to add song to
        if playlistName == "Default_Playlist":
            # Option to create a new playlist
            # Option to add to existing playlists
            pass
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
        self.windowOnTopFlag = True
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.windowOnTopFlag) # Set to stay on top
        self.setWindowTitle("Music Player")
        self.currentlyPlaying = 0
        self.musicCount = 10
        self.windowOnline = None
        self.windowPlaylists = None
        self.tableMusicDisplay = QTableWidget()
        self.tableMusicDisplay.setRowCount(self.musicCount)
        self.tableMusicDisplay.setColumnCount(4)
        self.tableMusicDisplay.setShowGrid(False)
        self.tableMusicDisplay.setHorizontalHeaderLabels(["Photo placeholder", "Audio Name", "Duration", "More Actions"]) # Only for debug

        for i in range(self.tableMusicDisplay.columnCount()):
            self.tableMusicDisplay.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            if i!=self.tableMusicDisplay.columnCount()-1:
                self.tableMusicDisplay.setEditTriggers(self.tableMusicDisplay.EditTrigger.NoEditTriggers)

        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        # Local library Song Search
        self.search_HorizontalLayout, self.searchBarVisibility = commonSearchBarAssets("Search", self.searchCurrentLibrary)

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutVertical = QVBoxLayout()
        widgetCentral.setLayout(layoutVertical)

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

        commonMenubarAssets(self) # Standardised Menubar assets

        self.volumeButton = QPushButton("Volume")
        self.volumeButton.clicked.connect(self.displayVolumeSlider)

        layoutPlayer.addWidget(QLabel()) # Name of the song/music/audio
        # layoutPlayer.addStretch()
        layoutPlayer.addWidget(self.volumeButton) # Volume control Button (Hidden - Volume control Slider )
        layoutPlayer.addWidget(QLabel()) # Current timestamp
        layoutPlayer.addWidget(self.sliderTime) # Time control Slider
        layoutPlayer.addWidget(QLabel()) # Duration of the song/music/audio
        layoutPlayer.addWidget(self.buttonPlay) # Play/Pause button

        layoutVertical.addLayout(self.search_HorizontalLayout)
        layoutVertical.addWidget(self.tableMusicDisplay)
        layoutVertical.addWidget(self.widgetPlayer)

        # --- Volume Slider ---
        self.volumeSlider = QSlider()
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setSliderPosition(100) # Default value
        self.volumeSlider.sliderMoved.connect(self.extraVolumeControl)
        self.volumeSlider.sliderReleased.connect(self.extraVolumeControl)
        self.volumeSlider.sliderPressed.connect(self.extraVolumeControl)
        self.volumeSlider.valueChanged.connect(self.extraVolumeControl)

        self.volumeSliderWidget = QWidget()
        self.volumeSliderWidget.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        volumeSliderWidget_layoutVertical = QVBoxLayout()
        self.volumeSliderWidget.setLayout(volumeSliderWidget_layoutVertical)
        volumeSliderWidget_layoutVertical.addWidget(self.volumeSlider)
        self.volumeSliderWidget.setVisible(False)

        self.windowName = "MainScreenWindow"

    def displayVolumeSlider(self):
        if self.volumeSliderWidget.isVisible():
            self.volumeSliderWidget.setVisible(False)
        else:
            parentPos = self.volumeButton.mapToGlobal(QPoint(0, -(self.volumeButton.height()+self.volumeSlider.height())))
            self.volumeSliderWidget.move(parentPos)
            self.volumeSliderWidget.setVisible(True)

    # def triggeredByAction(self, triggeringActionText:str):
    #     if "online" in triggeringActionText:
    #         print("Search Online")
    #         self.showOnlineWindow()
    #     elif "playlist" in triggeringActionText:
    #         print("Viewing Playlists")
    #         self.showPlaylistsWindow()
    #     else:
    #         pass

    def extraVolumeControl(self):
        # Function to control audio volume for extra finesse
        changedMultiplier = self.volumeSlider.value()/100
        self.audioOutput.setVolume(changedMultiplier)

    def searchCurrentLibrary(self):
        # TODO:
        # 1. Implement search logic
        # Make sure you don't search for empty strings
        # Not an empty string AND Not a string with spaces/tabs
        searchString : str = self.search_HorizontalLayout.itemAt(0).widget().text()
        if self.searchBarVisibility and searchString and not searchString.isspace():
            print(f"Searching for song {searchString} ...")
            self.searchBarVisibility = False
            self.search_HorizontalLayout.itemAt(0).widget().setVisible(self.searchBarVisibility)
            self.search_HorizontalLayout.itemAt(0).widget().clear()
        elif not self.searchBarVisibility:
            self.searchBarVisibility = True
            self.search_HorizontalLayout.itemAt(0).widget().setVisible(self.searchBarVisibility)
        else:
            # Search bar is already visible, but has no text to search for so
            # Do nothing
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

    def populateTable(self):
        self.detailsForTable = scan_and_return_songlist()
        self.musicCount = len(self.detailsForTable)
        self.tableMusicDisplay.setRowCount(self.musicCount) # Dynamically update based on table size
        for (i,musicDetails) in self.detailsForTable.items():
            buttonMoreActions = QPushButton("...")
            buttonMoreActions.setProperty("row_idx", i)
            buttonMoreActions.clicked.connect(self.moreActionsClicked)
            self.tableMusicDisplay.setItem(int(i), 1, QTableWidgetItem(musicDetails["fileName"]))
            self.tableMusicDisplay.setItem(int(i), 2, QTableWidgetItem(musicDetails["duration"]))
            self.tableMusicDisplay.setCellWidget(int(i), 3, buttonMoreActions)
            self.tableMusicDisplay.setRowHeight(int(i), 60)
            if i==self.musicCount-1:
                break
        self.selectedAudio(0, 1)
        self.buttonPlay.click()

    def moreActionsClicked(self):
        clicked_RowID = self.sender().property("row_idx")
        songDetails = self.detailsForTable[clicked_RowID]
        MA_Popup = MoreOptionsPopup(songDetails)
        MA_Pos = self.sender().mapToGlobal(QPoint(0, self.sender().height()))
        MA_Popup.displayPopup(MA_Pos)

    def selectedAudio(self, row, column):
        self.buttonPlay.setChecked(False)
        self.selectedAudioID = row
        if column != 3:
            self.mediaPlayer.setSource(QUrl().fromLocalFile(self.detailsForTable[row]["path"]))
            self.currentlyPlaying = row
            self.buttonPlay.click()
        time_vals = list(map(int, map(str.strip, self.detailsForTable[row]["duration"].split(":"))))
        audio_time_in_secs = 0
        if len(time_vals)>3:
            audio_time_in_secs += time_vals[0]*86400
        audio_time_in_secs += sum(val*(60**(len(time_vals)-1-idx)) for idx, val in enumerate(time_vals[-3:]))
        self.sliderTime.setRange(0, audio_time_in_secs*1000)
        self.widgetPlayer.layout().itemAt(0).widget().setText(self.detailsForTable[row]["fileName"])
        self.widgetPlayer.layout().itemAt(2).widget().setText("0 : 00") # TODO: Nice to haves (Non-Essential): Change dynamically based on length of audio as in -> 0:00 or 0:00:00 or 0:00:00:00
        self.widgetPlayer.layout().itemAt(4).widget().setText(self.detailsForTable[row]["duration"])

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
        self.windowOnTopFlag = True
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.windowOnTopFlag) # Set to stay on top
        self.setWindowTitle("Music Player")
        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")
        self.setWindowIcon(appIcon)

        self.windowHome = mainWindow

        commonMenubarAssets(self) # Standardised Menubar assets

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        layoutVertical = QVBoxLayout()
        widgetCentral.setLayout(layoutVertical)

        self.tablePlaylistDisplay = QTableWidget()
        self.tablePlaylistDisplay.setRowCount(1)
        self.tablePlaylistDisplay.setColumnCount(5)
        self.tablePlaylistDisplay.setShowGrid(False)
        self.tablePlaylistDisplay.setHorizontalHeaderLabels(["Photo placeholder", "Playlist Name", "Duration", "Songs", "More Actions"]) # Only for debug

        for i in range(self.tablePlaylistDisplay.columnCount()):
            self.tablePlaylistDisplay.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            if i!=self.tablePlaylistDisplay.columnCount()-1:
                self.tablePlaylistDisplay.setEditTriggers(self.tablePlaylistDisplay.EditTrigger.NoEditTriggers)

        layoutVertical.addWidget(self.tablePlaylistDisplay)

        self.populate_playlists()
        self.windowName = "PlaylistWindow"

    def populate_playlists(self):
        self.detailsForTable = list_playlists()
        self.playlistCount = len(self.detailsForTable)
        self.tablePlaylistDisplay.setRowCount(self.playlistCount) # Dynamically update based on table size
        for (i,playlistInfo) in self.detailsForTable.items():
            buttonMoreActions = QPushButton("...")
            buttonMoreActions.setProperty("row_idx", i)
            buttonMoreActions.clicked.connect(self.moreActionsClicked)
            self.tablePlaylistDisplay.setItem(int(i), 1, QTableWidgetItem(playlistInfo["playlistName"]))
            self.tablePlaylistDisplay.setItem(int(i), 2, QTableWidgetItem(playlistInfo["duration"]))
            self.tablePlaylistDisplay.setItem(int(i), 3, QTableWidgetItem(len(playlistInfo["audioPaths"])))
            self.tablePlaylistDisplay.setCellWidget(int(i), 4, buttonMoreActions)
            self.tablePlaylistDisplay.setRowHeight(int(i), 60)
            if i==self.playlistCount-1:
                break

    def moreActionsClicked(self):
        # Popup w/ options -> Edit Playlist, Delete Playlist
        clicked_RowID = self.sender().property("row_idx")
        playlistDetails = self.detailsForTable[clicked_RowID]
        # # MA_Popup = MoreOptionsPopup(songDetails)
        # MA_Pos = self.sender().mapToGlobal(QPoint(0, self.sender().height()))
        # # MA_Popup.displayPopup(MA_Pos)
        print(playlistDetails)
        return

# -----------------------------------------------------------------

class YoutubeWindow(QMainWindow):
    def __init__(self, mainWindow:QMainWindow | MainScreenWindow, parent=None):
        super(YoutubeWindow, self).__init__(parent)
        self.setGeometry(200, 200, 400, 200)
        self.windowOnTopFlag = True
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.windowOnTopFlag) # Set to stay on top
        self.setWindowTitle("Music Player")
        appIcon = QIcon("./Resources/Splash_Screen_Logo.png")
        self.setWindowIcon(appIcon)

        self.windowHome = mainWindow

        commonMenubarAssets(self) # Standardised Menubar Assets

        widgetCentral = QWidget()
        self.setCentralWidget(widgetCentral)
        # YouTube Song Search
        self.search_HorizontalLayout, _ = commonSearchBarAssets("Search YouTube...", self.searchSong, True)
        self.download_HorizontalLayout, _ = commonSearchBarAssets("Link to Download...", self.downloadAudio, True)
        layoutVertical = QVBoxLayout()
        widgetCentral.setLayout(layoutVertical)
        layoutVertical.addLayout(self.search_HorizontalLayout)
        layoutVertical.addLayout(self.download_HorizontalLayout)
        self.windowName = "YoutubeWindow"

    def searchSong(self):
        # TODO:
        # 1. Enable searchLineEdit when in focus and disable when search is clicked
        searchString : str = self.search_HorizontalLayout.itemAt(0).widget().text()
        if searchString and not searchString.isspace():
            print(f"Searching for song {searchString} ...")
            responseDict = youtube_search_logic(searchString)
            searchResultsTitle = [item["snippet"]["title"] for item in responseDict["items"]]
            print(searchResultsTitle)

    def downloadAudio(self):
        # TODO:
        # 1. Change default download folder to MUSIC_PATH from .env
        linkToDownloadString : str = self.download_HorizontalLayout.itemAt(0).widget().text()
        if linkToDownloadString and not linkToDownloadString.isspace():
            from yt_dlp import YoutubeDL
            # Test_URL = "https://www.youtube.com/watch?v=FhhA5purigQ"
            # To download straight to a file
            print(f"Downloading {linkToDownloadString} ...")
            ydl_options = {"format":"bestaudio[ext=m4a]/bestaudio/best"}
            with YoutubeDL(ydl_options) as ydl:
                ydl.download([linkToDownloadString])
            print("Download Done!...")

# -----------------------------------------------------------------

class AppWindows():
    def __init__(self):
        super(AppWindows, self).__init__()
        self.app = QApplication(sys.argv)
        # self.windowSplashScreen = SplashScreenWindow() # ---Undo Comment---
        self.windowMainScreen = MainScreenWindow()
        # self.getDetails()
        self.windowMainScreen.populateTable()
        # self.windowSplashScreen.delayForSometime(0.1) # ---Undo Comment---
        self.windowMainScreen.show()
        # self.windowSplashScreen.finish(self.windowMainScreen) #---Undo Comment---
        # del self.windowSplashScreen #---Undo Comment---
        # self.app.setStyleSheet(Path("./Resources/styleSheet.qss").read_text())
        sys.exit(self.app.exec())

    # def getDetails(self):
        # self.worker = Worker("get_song_list")
        # self.worker.start()
        # self.worker.finished.connect(self.windowMainScreen.populateTable)
        # self.worker.error.connect(self.windowMainScreen.handleError)

# -----------------------------------------------------------------

if __name__ == "__main__":
    AppWindows()