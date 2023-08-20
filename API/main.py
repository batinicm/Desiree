from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from Analyzer import recommender
from Analyzer.Utils import lyric_fetch_utils, storage_utils, analyzer_utils
from Analyzer.Model import constants
import random
from pydantic import BaseModel
from typing import List

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

        #num = random.choice([0, len(songs) - 15])
        #songs = songs[num:num+15]

        songs = songs[0:40]

        songs = list(map(API.utils.add_recommendations_for_web, songs))
        songs = list(filter(lambda s: s['Recommendations'] is not None and len(s['Recommendations']) > 0, songs))
        info = {
            'Title': playlist_info['Title'],
            'Description': playlist_info['Description'],
            'Songs': songs[0:8]
        }

        for song in info['Songs']:
            API.utils.expand_recommendation_info(song)

        playlists_info.append(info)

    return playlists_info


class RecommendationId(BaseModel):
    id: str


# Expand recommendations for a song by searching for full information
# Except the recommendations for the songs
@app.post('expandrecommendations')
async def expand_recommendations(recommendations: List[RecommendationId]):
    full_info = []
    for recommendation_id in recommendations:
        info = API.utils.get_song_info(recommendation_id)
        if info is None:
            continue

        full_info = full_info + info

    return full_info


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
