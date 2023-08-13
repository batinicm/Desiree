from Analyzer import recommender
from Analyzer.Utils import lyric_fetch_utils, storage_utils, analyzer_utils
from Analyzer.Model import constants
from Analyzer.Model.track_class import Track


def extract_info_for_webapp(track):
    extracted_track = track['track']
    image_href = [image['url'] for image in extracted_track['album']['images']][0]
    artist = [artist['name'] for artist in extracted_track['artists']][0]
    return {
        'ImageHref': image_href,
        'Name': extracted_track['name'],
        'Artist': artist,
        'Url': extracted_track['preview_url'],
        'SpotifyId': extracted_track['id']
    }


def get_recommendations(track):
    table_query_result = list(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))

    # If the song doesn't exist among the saved songs, the entire process of getting lyrics, analyzing the sentiment,
    # getting key phrases and tokenization needs to be done
    # Additionally, storing this new information in each of the tables
    # And finally, getting recommendations
    if len(table_query_result) == 0:
        try:
            lyrics = lyric_fetch_utils.get_lyrics(track)
            lyrics = analyzer_utils.prepare_scraped_lyrics_for_analysis([lyrics])
            storage_utils.store_lyrics(lyrics)

            lyrics = list(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))
            sentiment_analyzed = list(analyzer_utils.analyze_text(lyrics))
            storage_utils.store_sentiment(sentiment_analyzed)
            phrases = list(analyzer_utils.extract_key_phrases(lyrics))
            storage_utils.store_phrases(phrases)
            print("Done adding.")
        except:
            return []

    recommendations = recommender.recommend_in_existing(track.spotify_id)
    return recommendations


def add_recommendations_for_web(song):
    track = Track(spotify_id=song['SpotifyId'], name=song['Name'],
                  artists=[song['Artist']])
    recommendations = get_recommendations(track)

    song['Recommendations'] = recommendations
    return song
