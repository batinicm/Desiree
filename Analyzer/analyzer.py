# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import vault_worker
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

ALL_OUT_PLAYLIST_IDS = ['37i9dQZF1DX5Ejj0EkURtP', '37i9dQZF1DX4o1oenSJRJd', '37i9dQZF1DXbTxeAdrVG2l',
                        '37i9dQZF1DX4UtSsGT1Sbe']


# TODO: Use Spotify API to get playlist contents (aka songs in playlists)
# Dedupe song names
# Use song names (and artists?) to retrieve lyrics from Genius
# Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user experience)
# on retrieved lyrics
# ? Store result in Azure storage account for that

def extract_track_info(track):
    return {
        "Name": track['track']['name'],
        "Artists": [artist['name'] for artist in track['track']['artists']]
    }


# Get playlist contents
# Information to keep: track name, track artist
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
            all_tracks.append(items)

    return all_tracks


def get_lyrics():


def analyze_text(text):
    endpoint = vault_worker.get_secret("LanguageAnalyzerEndpoint")
    key = vault_worker.get_secret("LanguageAnalyzerKey")

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))


if __name__ == '__main__':
    get_tracks()
