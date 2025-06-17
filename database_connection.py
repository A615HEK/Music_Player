import mysql.connector as dbConn
from os import getenv
from dotenv import load_dotenv

# validateLogin(), getPatientTableInfo(), updatePACSDB() -> export panna podhum
load_dotenv()

databaseConnection = dbConn.connect(host=getenv("MYSQL_HOST"), user=getenv("MYSQL_USER"), password=getenv("MYSQL_PASSWORD"), database=getenv("MYSQL_DATABASE"))
myCursor = databaseConnection.cursor()

def initPlaylistsDB():
    """Initialize the DB for playlists and songs"""
    # TODO: Only if this is the first time in the device
    global myCursor
    myCursor.execute("CREATE DATABASE musicPlayerDB")
    myCursor.execute("CREATE TABLE songs_DB(songName VARCHAR(255), playlistName VARCHAR(255) PRIMARY KEY, addedOn DATE)")

def getAllPlaylists():
    """Returns the names of all playlists"""
    global myCursor
    myCursor.execute("SELECT playlist_name FROM songs_DB GROUP BY playlist_name HAVING COUNT(playlist_name) = 1")
    return list(myCursor)

# def getPlaylist(playlistName:str):
#     """Returns all songs in the playlist specified"""
#     global myCursor
#     myCursor.execute("SELECT * FROM songs_DB WHERE playlistName = %s", (playlistName,))
#     return list(myCursor)

def addPlaylist(playlistName:str):
    # Only a song can be added to a playlist
    # You can't create a playlist and then add songs to it
    global myCursor
    global databaseConnection
    if playlistName:
        # TODO:
        # 1. Add playlist photo
        queriesToExecute = ("INSERT INTO playlists_DB (playlistName, createdOn) VALUES (%s, CURRENT_DATE)")
        myCursor.execute(queriesToExecute, (playlistName,))
        databaseConnection.commit()
        print(f"Created new playlist {playlistName}...")
        return
    else:
        print("Enter a valid DB Name")
        return

# def getUser(enteredUserName: str, enteredPassword: str) -> str:
#     global myCursor
#     myCursor.execute("SELECT fullName FROM users WHERE userName = %s AND userPwd = %s", (enteredUserName, enteredPassword))
#     usernameValue = list(myCursor)
#     if (not usernameValue):
#         return "Invalid Login"
#     return usernameValue[0][0]

# def loginUpdate(loggedInUser: str) -> str:
#     global myCursor
#     myCursor.execute("UPDATE Users SET lastLogin = NOW() WHERE userName = %s", (loggedInUser,))
#     myCursor.execute("SELECT lastLogin FROM users WHERE userName = %s", (loggedInUser,))
#     return list(myCursor)[0][0].strftime("%d/%m/%Y, %H:%M:%S")

# def validateLogin(enteredUserName: str, enteredPassword: str):
#     userName =  getUser(enteredUserName, enteredPassword)
#     if (userName == "Invalid Login"):
#         return "invalidLogin"
#     loginTime =  loginUpdate(enteredUserName)
#     return {"fullName" : userName, "loginTime" : loginTime}

# def getPatientTableInfo(patientID: int = None) -> list[dict]:
#     global myCursor
#     if (not patientID):
#         myCursor.execute("SELECT * FROM pacs_database ORDER BY lastAccessedOn DESC LIMIT 20")
#     else:
#         myCursor.execute("SELECT * FROM pacs_database WHERE patientID = %s", (patientID,))
#     patRecords = list(myCursor)
#     patDetailsLabel = ["PatientID", "PatientName", "PatientDoB", "PatientSex", "ReferringDoctor", "Description", "DateOfStudy", "Modality", "DataPath", "TimeLastAccessed", "TimeRecordCreated"]
#     for i,patient in enumerate(patRecords):
#         patDetails = {}
#         for j,data in enumerate(patient):
#             patDetails[patDetailsLabel[j]] = data
#         patRecords[i] = patDetails
#     return patRecords

# def updateLastAccessed(patientID: str) -> None:
#     global myCursor
#     myCursor.execute("UPDATE PACS_database SET lastAccessedOn = NOW() WHERE patientID = %s", (patientID,))
#     print("Updated lastAccessedOn!")

# def updatePACSDB(patientData, newPatient: int) -> None:
#     """
#     For uploading and/or updating new/existing patient info to the database
#     """
#     global myCursor
#     if (newPatient):
#         print("Uploading new patient info to Database...")
#         queriesToExecute = ("INSERT INTO PACS_Database(patientID, patientName, patientDoB, patientSex, referringPhysician, studyDescription, studyDate, modality, dataPath)",
#                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
#         myCursor.execute(queriesToExecute, (patientData.PatientID, patientData.PatientName, patientData.PatientDoB, patientData.PatientSex, patientData.ReferringPhysician, patientData.StudyDescription, patientData.StudyDate, patientData.Modality, patientData.DataPath))
#     updateLastAccessed(patientData.PatientID)
#     if (newPatient):
#         print("Successfully updated PACS with new patient\'s info!")
