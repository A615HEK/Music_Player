from fastapi import FastAPI
from os import path, listdir
from tinytag import TinyTag
from time_Calcer import Time_Values
music_path = "C:/Abyss-heck/Paadalgal"

app = FastAPI()

@app.get("/")
async def root():
    songs = {}
    for i, song in enumerate(listdir(music_path)):
        audio = TinyTag.get(path.join(music_path, song))
        songs[i] = {"filename":song, "duration":Time_Values(audio.duration.__floor__()).__repr__(), "path":audio.filename}
    return songs