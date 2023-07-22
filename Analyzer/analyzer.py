# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them

from Utils import storage_utils, analyzer_utils, lyric_fetch_utils

ALL_OUT_PLAYLIST_IDS = ['37i9dQZF1DX5Ejj0EkURtP', '37i9dQZF1DX4o1oenSJRJd', '37i9dQZF1DXbTxeAdrVG2l',
                        '37i9dQZF1DX4UtSsGT1Sbe']
LYRICS_TABLE_NAME = 'Lyrics'
SENTIMENT_TABLE_NAME = 'Sentiments'

# TODO: Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user
#  experience) on retrieved lyrics
# TODO: opinion mining? How does it relate to recommendations?


if __name__ == '__main__':
    storage_utils.delete_entities(LYRICS_TABLE_NAME)

    if not storage_utils.check_storage_created(LYRICS_TABLE_NAME):
        for playlist in ALL_OUT_PLAYLIST_IDS:
            tracks = lyric_fetch_utils.get_tracks(playlist)
            lyrics = map(lyric_fetch_utils.get_lyrics, tracks[0:3])
            lyrics = analyzer_utils.prepare_lyrics_for_analysis(lyrics)
            storage_utils.store_lyrics(lyrics)

    lyrics = list(storage_utils.get_from_storage(LYRICS_TABLE_NAME))
    sentiment_analyzed = analyzer_utils.analyze_text(lyrics)
