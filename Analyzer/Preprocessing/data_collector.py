# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
from io import StringIO

import pandas

from Utils import storage_utils, analyzer_utils, lyric_fetch_utils
from Model import constants


# Get blob data and process it, so it fits storage schema
def get_kaggle_data():
    # Read data from Azure Blob - 2 csvs: artists and lyrics
    # Use only 'en' songs
    # Create data to go with the Lyrics table schema
    artist_data = storage_utils.get_from_blob('kaggle-lyrics', 'artists-data.csv')
    artists_df = pandas.read_csv(StringIO(artist_data.decode('utf-8')))

    lyrics_data = storage_utils.get_from_blob('kaggle-lyrics', 'lyrics-data-en.csv')
    lyrics_df = pandas.read_csv(StringIO(lyrics_data.decode('utf-8')))

    complete_data = pandas.merge(artists_df, lyrics_df, left_on='Link', right_on='ALink')
    complete_data.drop(['ALink', 'Genres', 'Link', 'Popularity', 'Songs', 'language'], axis=1, inplace=True)
    complete_data.rename(columns = {'Artist': 'Artists', 'Lyric': 'Lyrics', 'SLink': 'SpotifyId', 'SName': 'Name' }, inplace = True)

    return complete_data


if __name__ == '__main__':
    # storage_utils.delete_entities(LYRICS_TABLE_NAME)
    # storage_utils.delete_entities(SENTIMENT_TABLE_NAME)
    # storage_utils.delete_entities(PHRASES_TABLE_NAME)

        # Prepare kaggle data
    kaggle_data = get_kaggle_data()
    analyzer_utils.prepare_kaggle_lyrics_for_analysis(kaggle_data)
    storage_utils.store_lyrics(kaggle_data)

    if not storage_utils.check_storage_created(constants.LYRICS_TABLE_NAME):
        # Prepare scraped material
        for playlist in constants.ALL_OUT_PLAYLIST_IDS:
            tracks = lyric_fetch_utils.get_tracks(playlist)
            lyrics = map(lyric_fetch_utils.get_lyrics, tracks[0:3])
            lyrics = analyzer_utils.prepare_scraped_lyrics_for_analysis(lyrics)
            storage_utils.store_lyrics(lyrics)

    lyrics = list(storage_utils.get_from_storage(constants.LYRICS_TABLE_NAME))
    sentiment_analyzed = list(analyzer_utils.analyze_text(lyrics))
    storage_utils.store_sentiment(sentiment_analyzed)
    phrases = list(analyzer_utils.extract_key_phrases(lyrics))
    storage_utils.store_phrases(phrases)

