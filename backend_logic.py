from fastapi import FastAPI
from os import path, listdir
music_path = "C:/Abyss-heck/Paadalgal"

app = FastAPI()

@app.get("/")
def root():
    song_paths = {}
    for i, song in enumerate(listdir(music_path)):
        if i<10:
            song_paths[i] = path.join(music_path, song)
    return song_paths