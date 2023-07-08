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

ALL_OUT_PLAYLIST_IDS = ['37i9dQZF1DX5Ejj0EkURtP', '37i9dQZF1DX4o1oenSJRJd', '37i9dQZF1DXbTxeAdrVG2l',
                        '37i9dQZF1DX4UtSsGT1Sbe']

LYRICS_TABLE_NAME = 'Lyrics'

# Use Spotify API to get playlist contents (aka songs in playlists)
# Dedupe song names
# Use song names (and artists?) to retrieve lyrics from Genius
# TODO: Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user experience)
# on retrieved lyrics
# ? Store result in Azure storage account for that

# Extract necessary information from the track information retrieved from Spotify
def extract_track_info(track):
    return Track(spotify_id=track['track']['id'], name=track['track']['name'], artists=[artist['name'] for artist in track['track']['artists']])


# Get playlist contents
def get_tracks():
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    all_tracks = []

    for playlist_id in ALL_OUT_PLAYLIST_IDS:
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
    return all_tracks


# Purge 'feat.' from song titles, since it impacts search results on Genius
def purge_feat_from_title(title):
    return re.sub(".feat.*", "", title)


# Get lyrics to songs using Genius API
def get_lyrics(track):
    genius_token = vault_worker.get_secret("GeniusClientAccessToken")

    genius = Genius(genius_token)
    artist = genius.search_artist(next(iter(track.artists or [])), max_songs=0)

    song_title = purge_feat_from_title(track.name)
    song = genius.search_song(song_title, artist.name)

    if song is None:
        raise Exception("Song not found")

    track.lyrics = song.lyrics
    return track


# Preprocess lyrics to eliminate part of song annotations (verse, chorus, singer...)
# and additional details at the beginning of the song
def prepare_for_analysis(track):
    lyrics = re.sub("\[.*\]", "", track.lyrics)
    lyrics = lyrics.split("\n")
    track.lyrics = "\n".join(lyrics[1:- 1])

    return track


# Check if any track has been written to the storage: if yes, no additional querying of Spotify/Genius is needed
# in order to obtain track names, artists and lyrics
def check_storage_created():
    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name=LYRICS_TABLE_NAME)
    entities = table_client.query_entities(query_filter="PartitionKey ne ''", results_per_page=1)
    return len(list(entities)) != 0


# Partition key: first artist name
# Row key: song spotify id - from the class itself (id.name? for easier search?)
def store_single_track(track, table_client):
    table_entity = {
        u'PartitionKey': next(iter(track.artists or [])),
        u'RowKey': track.spotify_id,
        u'TrackName': track.name,
        u'Artists': ",".join(track.artists),
        u'Lyrics': track.lyrics
    }
    table_client.create_entity(entity=table_entity)


# Store song with lyrics in Azure Storage Account
def store_lyrics(lyrics):
    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name=LYRICS_TABLE_NAME)

    for lyric in lyrics:
        store_single_track(lyric, table_client)


def analyze_text(text):
    endpoint = vault_worker.get_secret("LanguageAnalyzerEndpoint")
    key = vault_worker.get_secret("LanguageAnalyzerKey")

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))


if __name__ == '__main__':

    if not check_storage_created():
        tracks = get_tracks()
        lyrics = map(get_lyrics, tracks)
        lyrics = map(prepare_for_analysis, lyrics)
        store_lyrics(lyrics)
