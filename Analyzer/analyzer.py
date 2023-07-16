# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import vault_worker
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from lyricsgenius import Genius
import re
from azure.data.tables import TableServiceClient
from Model.track_class import Track
import pandas
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

ALL_OUT_PLAYLIST_IDS = ['37i9dQZF1DX5Ejj0EkURtP', '37i9dQZF1DX4o1oenSJRJd', '37i9dQZF1DXbTxeAdrVG2l',
                        '37i9dQZF1DX4UtSsGT1Sbe']
LYRICS_TABLE_NAME = 'Lyrics'
BATCH_OPERATION_COUNT = 20
LYRICS_TABLE_ENTITY_COLUMNS = ['Partition', 'RowKey', 'TrackName', 'Artists', 'Lyrics']


# Use Spotify API to get playlist contents (aka songs in playlists)
# Dedupe song names
# Use song names (and artists?) to retrieve lyrics from Genius
# TODO: Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user experience)
# on retrieved lyrics
# ? Store result in Azure storage account for that

# Extract necessary information from the track information retrieved from Spotify
def extract_track_info(track):
    return Track(spotify_id=track['track']['id'], name=track['track']['name'],
                 artists=[artist['name'] for artist in track['track']['artists']])


# Get playlist contents
def get_tracks(playlist_id):
    print("Starting get_tracks:")

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    all_tracks = []

    pl_id = 'spotify:playlist:' + playlist_id
    offset = 0
    while True:
        response = sp.playlist_items(pl_id,
                                     offset=offset,
                                     fields='items',
                                     additional_types=['track'])
        if len(response['items']) == 0:
            break

        items = list(map(extract_track_info, response['items']))
        print(items)
        offset = offset + len(items)
        all_tracks = all_tracks + items

    print("Total song number: " + str(len(all_tracks)))
    print("get_tracks done.")
    return all_tracks


# Purge 'feat.' from song titles, since it impacts search results on Genius
def purge_feat_from_title(title):
    return re.sub(".feat.*", "", title)


# Get lyrics to songs using Genius API
def get_lyrics(track):
    print("Fetching lyrics")
    genius_token = vault_worker.get_secret("GeniusClientAccessToken")

    genius = Genius(access_token=genius_token, sleep_time=1, retries=5)
    artist = genius.search_artist(next(iter(track.artists or [])), max_songs=0)

    song_title = purge_feat_from_title(track.name)
    song = genius.search_song(song_title, artist.name)

    if song is None:
        track.lyrics = ""
    else:
        track.lyrics = song.lyrics

    print("Lyrics fetched")
    return track


# Preprocess lyrics to eliminate part of song annotations (verse, chorus, singer...)
# and additional details at the beginning of the song
def process_lyrics_for_analysis(lyrics):
    cleaned_lyrics = re.sub("\[.*\]", "", lyrics)
    cleaned_lyrics = cleaned_lyrics.split("\n")
    return "\n".join(cleaned_lyrics[1:- 1])


# Remove duplicate songs (recognized by the same spotify guid)
# Remove rows which have empty 'Lyrics' column
# Prepare lyrics for analysis
def prepare_for_analysis(tracks):
    dataframe = pandas.DataFrame(map(Track.to_dict, tracks))
    print(dataframe)

    dataframe.drop_duplicates(subset=['SpotifyId'], inplace=True)
    print(dataframe)

    dataframe['Lyrics'].str.strip()
    dataframe.drop(dataframe[dataframe['Lyrics'] == ""].index, inplace=True)
    print(dataframe)

    dataframe['Lyrics'] = list(map(process_lyrics_for_analysis, dataframe['Lyrics']))
    return dataframe


# Check if any track has been written to the storage: if yes, no additional querying of Spotify/Genius is needed
# in order to obtain track names, artists and lyrics
def check_storage_created():
    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name=LYRICS_TABLE_NAME)
    entities = table_client.query_entities(query_filter="PartitionKey ne ''", results_per_page=1)
    return len(list(entities)) != 0


def delete_entities():
    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name=LYRICS_TABLE_NAME)
    entities = table_client.query_entities(query_filter="PartitionKey ne ''")

    for entity in entities:
        table_client.delete_entity(entity["PartitionKey"], entity["RowKey"])


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
    print("Store lyrics started")

    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name=LYRICS_TABLE_NAME)

    operations = pandas.DataFrame()
    operations['PartitionKey'] = list(map(get_partition_key, tracks['Artists']))
    operations['Operation'] = list(map(create_lyric_table_operation, tracks.iterrows()))

    # After groupby - list of table_entity for each partition key
    grouped = operations.groupby('PartitionKey').agg(list)

    for _, group in grouped.iterrows():
        table_client.submit_transaction(group['Operation'])

    print("Lyrics stored")


def analyze_text(text):
    endpoint = vault_worker.get_secret("LanguageAnalyzerEndpoint")
    key = vault_worker.get_secret("LanguageAnalyzerKey")

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))


if __name__ == '__main__':
    # delete_entities()

    if not check_storage_created():
        for playlist in ALL_OUT_PLAYLIST_IDS:
            tracks = get_tracks(playlist)
            lyrics = map(get_lyrics, tracks)
            lyrics = prepare_for_analysis(lyrics)
            store_lyrics(lyrics)
