from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from Analyzer import recommender
from Analyzer.Utils import lyric_fetch_utils, storage_utils, analyzer_utils
from Analyzer.Model import constants
import random

import API.utils

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Functionalities we want:
#   - search for a song by name and return 11 songs to play: the searched songs and top 10 similar songs to play next
@app.get("/")
async def home():
    return "Hello, World!"


@app.get("/topplaylists")
async def home_playlists_fetch():
    playlists_info = []

    for playlist_id in constants.ALL_OUT_PLAYLIST_IDS:
        playlist_info = lyric_fetch_utils.get_playlist_info(playlist_id)
        tracks = lyric_fetch_utils.get_playlist_items(playlist_id)
        songs = list(map(API.utils.extract_info_for_webapp, tracks))

        songs = list(filter(lambda s: s['Url'] is not None, songs))

        #TODO: remove
        num = random.choice([0, len(songs) - 15])
        songs = songs[num:num+15]

        songs = list(map(API.utils.add_recommendations_for_web, songs))
        songs = list(filter(lambda s: len(s['Recommendations']) > 0, songs))
        info = {
            'Title': playlist_info['Title'],
            'Description': playlist_info['Description'],
            'Songs': songs[0:10]
        }
        playlists_info.append(info)

    return playlists_info


@app.get("/song/{song_name}&{artist}")
async def get_songs(song_name, artist):
    track = lyric_fetch_utils.get_track(song_name, artist)
    if track == "":
        return

    return API.utils.get_recommendations(track)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
