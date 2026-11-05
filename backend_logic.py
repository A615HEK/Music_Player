from os import path, listdir, getenv
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

def youtube_search_logic(searchString : str) -> dict:
    """Returns the default YouTube response dictionary"""
    YouTubeService = build("youtube", "v3", developerKey=getenv("YOUTUBE_API_KEY"))
    results = YouTubeService.search().list(part="snippet", q=searchString)
    responseDict = results.execute()
    return responseDict