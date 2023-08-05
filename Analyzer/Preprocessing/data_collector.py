from io import StringIO
import pandas

from Utils import storage_utils, analyzer_utils, lyric_fetch_utils
from Model import constants


# Kaggle data is stored in an Azure Storage Blob
# Original data link: https://www.kaggle.com/datasets/neisse/scrapped-lyrics-from-6-genres?resource=download&select=lyrics-data.csv
# The original data contained ~70k songs/lyrics, so we narrow the scope down by using only songs which have 'en' as language
# Get data from blob, process it, so it fits destination Azure table schema
def get_kaggle_data():
    artist_data = storage_utils.get_from_blob('kaggle-lyrics', 'artists-data.csv')
    artists_df = pandas.read_csv(StringIO(artist_data.decode('utf-8')))

    lyrics_data = storage_utils.get_from_blob('kaggle-lyrics', 'lyrics-data-en.csv')
    lyrics_df = pandas.read_csv(StringIO(lyrics_data.decode('utf-8')))

    complete_data = pandas.merge(artists_df, lyrics_df, left_on='Link', right_on='ALink')
    complete_data.drop(['ALink', 'Genres', 'Link', 'Popularity', 'Songs', 'language'], axis=1, inplace=True)
    complete_data.rename(columns = {'Artist': 'Artists', 'Lyric': 'Lyrics', 'SLink': 'SpotifyId', 'SName': 'Name' }, inplace = True)

    return complete_data


# For the offline part of the application, we create the initial dataset by using 2 methods of data collection:
#   1. Scraping Spotify and Genius lyrics
#   2. Pre-compiled list of lyrics from Kaggle
if __name__ == '__main__':
    if not storage_utils.check_storage_created(constants.LYRICS_TABLE_NAME):
        for playlist in constants.ALL_OUT_PLAYLIST_IDS:
            tracks = lyric_fetch_utils.get_tracks(playlist)
            lyrics = map(lyric_fetch_utils.get_lyrics, tracks)
            lyrics = analyzer_utils.prepare_scraped_lyrics_for_analysis(lyrics)
            storage_utils.store_lyrics(lyrics)

        kaggle_data = get_kaggle_data()
        analyzer_utils.prepare_kaggle_lyrics_for_analysis(kaggle_data)
        storage_utils.store_lyrics(kaggle_data)

    lyrics = list(storage_utils.get_from_storage(constants.LYRICS_TABLE_NAME))
    sentiment_analyzed = list(analyzer_utils.analyze_text(lyrics))
    storage_utils.store_sentiment(sentiment_analyzed)
    phrases = list(analyzer_utils.extract_key_phrases(lyrics))
    storage_utils.store_phrases(phrases)

