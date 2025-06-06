from fastapi import FastAPI
from os import path, listdir
music_path = "C:/Abyss-heck/Paadalgal"

app = FastAPI()

@app.get("/")
async def root():
    song_paths = {}
    songs = {}
    for i, song in enumerate(listdir(music_path)):
        # if i<10:
            # song_paths[i] = path.join(music_path, song)
        songs[i] = song
    return songs