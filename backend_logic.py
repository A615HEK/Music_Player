from os import path, listdir, getenv, remove
from tinytag import TinyTag
from time_Calcer import Time_Values
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()

# Global variables
audioPath = getenv("AUDIO_PATH")
playlistPath = getenv("PLAYLIST_PATH")

def scan_and_return_songlist():
    songs = {}
    for i, song in enumerate(listdir(audioPath)):
        audio = TinyTag.get(path.join(audioPath, song))
        songs[i] = {
            "fileName":song,
            "duration":Time_Values(audio.duration.__floor__()).__repr__(),
            "path":audio.filename
            }
    return songs

# --- Playlist Logic ---

def list_playlists():
    playlists = {}
    for i, playlistFile in enumerate(listdir(playlistPath)):
        # CONTINUE:
        playlistFilePath = (playlistPath+"/"+playlistFile)
        with open(playlistFilePath) as p:
            playlistContents = p.readlines()
            playlistAudioPaths = playlistContents[2::2]
        playlists[i] = {
            "playlistName":playlistFile[:-5], # Slicing away .m3u8
            "audioPaths":playlistAudioPaths,
            "duration":Time_Values(100).__repr__()
            }
    return playlists

def new_playlist(playlistName:str):
    pName = playlistPath+playlistName+".m3u8"
    if not path.exists(pName):
        # create a new playlist
        with open(pName, "w") as f:
            f.write("#EXTM3U\n")
    else:
        # Warning and let person edit -> Playlist name exists!
        print(f"Error: Trying to create an existent playlist; Playlist: {playlistName} already exists!...")
        return
    pass

def edit_playlist(playlistName:str, operationToDo:str, songDetails:dict):
    """
    operationToDo -> ADD_SONGS, DELETE_SONGS (1st priority)
    operationToDo -> REORDER_SONGS (next priority)
    New Playlist can't be created without atleast 1 song (for now, let's see how it goes)
    """
    # TODO:
    # 1. Finish implementing delete capability
    songName = songDetails["fileName"]
    SUPPORTED_OPERATIONS = ["ADD_SONGS", "DELETE_SONGS", "REORDER_SONGS"]
    if playlistName.isspace():
        print("Error: Enter a valid playlist name not spaces bruv!")
        return
    if operationToDo not in SUPPORTED_OPERATIONS:
        print(f"Error: Non-existent operation; Operation: {operationToDo} is unsupported!...")
        return
    # Only runs if playlist name exists and operation is supported
    pName = playlistPath+playlistName+".m3u8"
    # Check if playlist exists: If False and Songs to be added -> Create Playlist; Else -> Error
    if not path.exists(pName):
        if operationToDo == "ADD_SONGS":
            new_playlist(playlistName)
        else:
            print(f"Error: Trying to update a non-existent playlist; Playlist: {playlistName} doesn't exist!...")
            return
    # Now that the playlist exists and specified operation is supported
    # Do appropriate operation on playlist
    if operationToDo == "ADD_SONGS" and songName:
        print(f"Playlist Updated: Added {songName} to {playlistName}")
        with open(pName, "a") as f:
            time_vals = list(map(int, map(str.strip, songDetails["duration"].split(":"))))
            DURATION = 0
            if len(time_vals)>3:
                DURATION += time_vals[0]*86400
            DURATION += sum(val*(60**(len(time_vals)-1-idx)) for idx, val in enumerate(time_vals[-3:]))
            f.write(F"#EXTINF:{DURATION}\n")
            f.write(songDetails["path"])
            pass

    elif operationToDo == "DELETE_SONGS" and songName:
        print(f"Playlist Updated: Deleted {songName} from {playlistName}")
        pass
    # elif operationToDo == "REORDER_SONGS":
    #     print(f"Playlist Updated: Added {songName} to {playlistName}")
    #     pass

def delete_playlist(playlistName:str):
    pName = playlistPath+playlistName+".m3u8"
    if path.exists(pName):
        remove(pName)
    else:
        print(f"Error: Trying to delete a non-existent playlist; Playlist: {playlistName} doesn't exist!...")
    pass

# --- End Playlist Logic ---

def youtube_search_logic(searchString : str) -> dict:
    """Returns the default YouTube response dictionary"""
    YouTubeService = build("youtube", "v3", developerKey=getenv("YOUTUBE_API_KEY"))
    results = YouTubeService.search().list(part="snippet", q=searchString)
    responseDict = results.execute()
    return responseDict