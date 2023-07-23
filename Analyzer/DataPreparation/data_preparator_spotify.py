# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them

from Utils import storage_utils, analyzer_utils, lyric_fetch_utils
from Model import constants

# TODO: Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user
#  experience) on retrieved lyrics
# TODO: opinion mining? How does it relate to recommendations?


if __name__ == '__main__':
    # storage_utils.delete_entities(LYRICS_TABLE_NAME)
    # storage_utils.delete_entities(SENTIMENT_TABLE_NAME)
    # storage_utils.delete_entities(PHRASES_TABLE_NAME)

    if not storage_utils.check_storage_created(constants.LYRICS_TABLE_NAME):
        for playlist in constants.ALL_OUT_PLAYLIST_IDS:
            tracks = lyric_fetch_utils.get_tracks(playlist)
            lyrics = map(lyric_fetch_utils.get_lyrics, tracks[0:3])
            lyrics = analyzer_utils.prepare_lyrics_for_analysis(lyrics)
            storage_utils.store_lyrics(lyrics)

    lyrics = list(storage_utils.get_from_storage(constants.LYRICS_TABLE_NAME))
    sentiment_analyzed = list(analyzer_utils.analyze_text(lyrics))
    storage_utils.store_sentiment(sentiment_analyzed)
    phrases = list(analyzer_utils.extract_key_phrases(lyrics))
    storage_utils.store_phrases(phrases)

