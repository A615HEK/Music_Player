from os import path, listdir, getenv, remove
from tinytag import TinyTag
from time_Calcer import Time_Values
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()

music_path = getenv("MUSIC_PATH")

def scan_and_return_songlist():
    songs = {}
    for i, song in enumerate(listdir(music_path)):
        audio = TinyTag.get(path.join(music_path, song))
        songs[i] = {
            "filename":song,
            "duration":Time_Values(audio.duration.__floor__()).__repr__(),
            "path":audio.filename
            }
    return songs

# --- Playlist Logic ---

def new_playlist(playlistName:str):
    pName = playlistName+".m3u8"
    if not path.exists(pName):
        # create new_playlist
        with open(pName, "w") as f:
            f.write("#EXTM3U\n")
        pass
    else:
        # Warning and let person edit -> Playlist name exists!
        print(f"Error: Trying to create an existent playlist; Playlist: {playlistName} already exists!...")
        return
    pass

def edit_playlist(playlistName:str, operationToDo:str, songName:str|None = None):
    "operationToDo -> ADD_SONGS, DELETE_SONGS, REORDER_SONGS"
    pName = playlistName+".m3u8"
    # Check if playlist exists
    if not path.exists(pName):
        print(f"Error: Trying to update a non-existent playlist; Playlist: {playlistName} doesn't exist!...")
        return
    # Now that the playlist exists, check if specified operation is supported
    if operationToDo == "ADD_SONGS" and songName:
        print(f"Playlist Updated: Added {songName} to {playlistName}")
        pass
    elif operationToDo == "DELETE_SONGS" and songName:
        print(f"Playlist Updated: Deleted {songName} from {playlistName}")
        pass
    elif operationToDo == "REORDER_SONGS":
        print(f"Playlist Updated: Added {songName} to {playlistName}")
        pass
    else:
        print(f"Error: Non-existent operation; Operation: {operationToDo} doesn't exist!...")
        return
    # Do appropriate operation on playlist
    with open(pName, "a") as f:
        # f.write(F"#EXTINF:{DURATION}\n")
        # f.write(musicFilePath)
        pass

def delete_playlist(playlistName:str):
    pName = playlistName+".m3u8"
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