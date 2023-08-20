import pandas

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
    lyrics_table_query_result = list(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))
    sentiment_table_query_result = list(
        storage_utils.get_from_table(constants.SENTIMENT_TABLE_NAME, rowkey=track.spotify_id))
    phrases_table_query_result = list(
        storage_utils.get_from_table(constants.PHRASES_TABLE_NAME, rowkey=track.spotify_id))

    # If the song doesn't exist among the saved songs, the entire process of getting lyrics, analyzing the sentiment,
    # getting key phrases and tokenization needs to be done
    # Additionally, storing this new information in each of the tables
    # And finally, getting recommendations
    if len(lyrics_table_query_result) == 0 or len(sentiment_table_query_result) == 0 or len(
            phrases_table_query_result) == 0:

        if (len(lyrics_table_query_result)) == 0:
            lyrics = lyric_fetch_utils.get_lyrics(track)
            if len(lyrics.lyrics) == 0:
                return

            lyrics = analyzer_utils.prepare_scraped_lyrics_for_analysis([lyrics])
            if not storage_utils.store_lyrics(lyrics):
                return

        lyrics = pandas.DataFrame(storage_utils.get_from_table(constants.LYRICS_TABLE_NAME, rowkey=track.spotify_id))
        lyrics.rename(columns={'RowKey': 'SpotifyId'}, inplace=True)

        if len(sentiment_table_query_result) == 0:
            sentiment_analyzed = analyzer_utils.analyze_text(lyrics)
            if not storage_utils.store_sentiment(sentiment_analyzed):
                storage_utils.delete_entity_from_all_tables(lyrics['PartitionKey'], lyrics['SpotifyId'])
                return

        if len(phrases_table_query_result) == 0:
            phrases = analyzer_utils.extract_key_phrases(lyrics)
            if not storage_utils.store_phrases(phrases):
                storage_utils.delete_entity_from_all_tables(lyrics['PartitionKey'], lyrics['SpotifyId'])
                return
        print("Done adding.")

    recommendations = recommender.recommend_in_existing(track.spotify_id)
    return recommendations


def add_recommendations_for_web(song):
    track = Track(spotify_id=song['SpotifyId'], name=song['Name'],
                  artists=[song['Artist']])
    recommendations = get_recommendations(track)

    song['Recommendations'] = recommendations
    return song


# Get song ImageHref, Name, Artist, Url, SpotifyId
def get_song_info(recommendation_id):
    raw_data = lyric_fetch_utils.get_track_by_id(recommendation_id)

    if raw_data is None:
        return None

    image_href = [image['url'] for image in raw_data['album']['images']][0]
    artist = [artist['name'] for artist in raw_data['artists']][0]
    return {
        'ImageHref': image_href,
        'Name': raw_data['name'],
        'Artist': artist,
        'Url': raw_data['preview_url'],
        'SpotifyId': raw_data['id']
    }


def expand_recommendation_info(song):
    full_info = []

    for recommendation_id in song['Recommendations']:
        info = get_song_info(recommendation_id)
        full_info.append(info)

    song['Recommendations'] = full_info
    return song
