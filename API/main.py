from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import recommender
from Analyzer.Utils import lyric_fetch_utils, storage_utils, analyzer_utils
from Analyzer.Model import constants

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
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


# Get song id from spotify
# Check if song already in storage
# If yes, find top 10 songs using already computed tokens
# If not, find artist from spotify search, use that to get genius lyrics and do the rest of the text processing to
# get top 10 similar songs
# Return an array of spotify ids for songs (be careful about the non-spotify songs in the corpus)
@app.get("/song/{song_name}&{artist}")
async def get_songs(song_name, artist):
    track = lyric_fetch_utils.get_track(song_name, artist)

    if track == "":
        return

    table_query_result = list(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))

    # If the song doesn't exist among the saved songs, the entire process of getting lyrics, analyzing the sentiment,
    # getting key phrases and tokenization needs to be done
    # Additionally, storing this new information in each of the tables
    # And finally, getting recommendations
    if len(table_query_result) == 0:
        lyrics = lyric_fetch_utils.get_lyrics(track)
        lyrics = analyzer_utils.prepare_scraped_lyrics_for_analysis([lyrics])
        storage_utils.store_lyrics(lyrics)

        lyrics = list(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))
        sentiment_analyzed = list(analyzer_utils.analyze_text(lyrics))
        storage_utils.store_sentiment(sentiment_analyzed)
        phrases = list(analyzer_utils.extract_key_phrases(lyrics))
        storage_utils.store_phrases(phrases)
        print("Done adding.")

    recommendations = recommender.recommend_in_existing(track.spotify_id)
    return recommendations


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
