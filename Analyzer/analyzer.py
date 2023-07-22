# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
import re

import pandas
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

import vault_utils
import storage_utils
import lyric_fetch_utils
from Model.track_class import Track

ALL_OUT_PLAYLIST_IDS = ['37i9dQZF1DX5Ejj0EkURtP', '37i9dQZF1DX4o1oenSJRJd', '37i9dQZF1DXbTxeAdrVG2l',
                        '37i9dQZF1DX4UtSsGT1Sbe']
LYRICS_TABLE_NAME = 'Lyrics'
LYRICS_TABLE_ENTITY_COLUMNS = ['Partition', 'RowKey', 'TrackName', 'Artists', 'Lyrics']
BATCH_OPERATION_COUNT = 20
SENTIMENT_TABLE_NAME = 'Sentiments'
SENTIMENT_TABLE_ENTITY_COLUMNS = ['Partition', 'RowKey', 'Sentiment']


# TODO: Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user experience)
# on retrieved lyrics


# Preprocess lyrics to eliminate part of song annotations (verse, chorus, singer...)
# and additional details at the beginning of the song
def process_lyrics_for_analysis(lyrics):
    cleaned_lyrics = re.sub("\[.*\]", "", lyrics)
    cleaned_lyrics = cleaned_lyrics.split("\n")
    return ".".join(cleaned_lyrics[1:- 1])


# Remove duplicate songs (recognized by the same spotify guid)
# Remove rows which have empty 'Lyrics' column
# Prepare lyrics for analysis
def prepare_lyrics_for_analysis(tracks):
    dataframe = pandas.DataFrame(map(Track.to_dict, tracks))
    print(dataframe)

    dataframe.drop_duplicates(subset=['SpotifyId'], inplace=True)
    print(dataframe)

    dataframe['Lyrics'].str.strip()
    dataframe.drop(dataframe[dataframe['Lyrics'] == ""].index, inplace=True)
    print(dataframe)

    dataframe['Lyrics'] = list(map(process_lyrics_for_analysis, dataframe['Lyrics']))
    return dataframe


def get_partition_key(artists):
    artist = next(iter(artists or []))
    artist = artist.replace('\\', '')
    artist = artist.replace('/', '')
    return artist


# Partition key: first artist name
# Row key: song spotify id - from the class itself (id.name? for easier search?)
def create_lyric_table_operation(track_row):
    track_info = track_row[1]
    return ('upsert', {
        u'PartitionKey': get_partition_key(track_info['Artists']),
        u'RowKey': track_info['SpotifyId'],
        u'Name': track_info['Name'],
        u'Artists': ",".join(track_info['Artists']),
        u'Lyrics': track_info['Lyrics']
    })


# Store song with lyrics in Azure Storage Account
def store_lyrics(tracks):
    operations = pandas.DataFrame()
    operations['PartitionKey'] = list(map(get_partition_key, tracks['Artists']))
    operations['Operation'] = list(map(create_lyric_table_operation, tracks.iterrows()))

    grouped = operations.groupby('PartitionKey').agg(list)

    for _, group in grouped.iterrows():
        storage_utils.store_transaction(LYRICS_TABLE_NAME, group['Operation'])


def get_max_score_sentiment(l):
    if (l.confidence_scores.positive >= l.confidence_scores.negative) and (
            l.confidence_scores.positive >= l.confidence_scores.neutral):
        return "positive"
    elif (l.confidence_scores.negative >= l.confidence_scores.positive) and (
            l.confidence_scores.negative >= l.confidence_scores.neutral):
        return "negative"
    else:
        return "neutral"


# TODO: storage: new table with same partition and row key as in Lyrics table
# Store overall sentiment: by examining the confidence scores and determining the max one
# Store sentence target and sentiment ?? sentiment of target is also max of confidence scores
def analyze_text(lyrics):
    endpoint = vault_utils.get_secret("LanguageAnalyzerEndpoint")
    key = vault_utils.get_secret("LanguageAnalyzerKey")
    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))

    lyrics_for_analysis = map(
        lambda lyric: {"PartitionKey": lyric["PartitionKey"], "RowKey": lyric["RowKey"], "Lyrics": lyric["Lyrics"]},
        lyrics)

    for entity in lyrics_for_analysis:
        result = text_analytics_client.analyze_sentiment([entity["Lyrics"]], show_opinion_mining=True)
        lyric_result = [l for l in result if not l.is_error]

        for l in lyric_result:
            sentiment = get_max_score_sentiment(l)


if __name__ == '__main__':
    storage_utils.delete_entities(LYRICS_TABLE_NAME)

    if not storage_utils.check_storage_created(LYRICS_TABLE_NAME):
        for playlist in ALL_OUT_PLAYLIST_IDS:
            tracks = lyric_fetch_utils.get_tracks(playlist)
            lyrics = map(lyric_fetch_utils.get_lyrics, tracks)
            lyrics = prepare_lyrics_for_analysis(lyrics)
            store_lyrics(lyrics)

    lyrics = list(storage_utils.get_from_storage(LYRICS_TABLE_NAME))
    analyze_text(lyrics)
