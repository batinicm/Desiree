import re

from lyricsgenius import Genius
import spotipy
from spotipy import SpotifyClientCredentials

from . import vault_utils
from Analyzer.Model.track_class import Track


# Extract necessary information from the track information retrieved from Spotify
def extract_track_info(track):
    return Track(spotify_id=track['track']['id'], name=track['track']['name'],
                 artists=[artist['name'] for artist in track['track']['artists']])


def extract_track_info_raw(track):
    return Track(spotify_id=track['id'], name=track['name'],
                 artists=[artist['name'] for artist in track['artists']])


def get_client_credentials():
    spotipy_client_id = vault_utils.get_secret("SpotifyClientId")
    spotipy_client_secret = vault_utils.get_secret("SpotifyClientSecret")

    return SpotifyClientCredentials(client_id=spotipy_client_id, client_secret=spotipy_client_secret)


def get_playlist_info(playlist_id):
    sp = spotipy.Spotify(client_credentials_manager=get_client_credentials())
    response = sp.playlist(playlist_id=playlist_id)

    return {
        'Title': response['name'],
        'Description': response['description']
    }


def get_playlist_items(playlist_id):
    sp = spotipy.Spotify(client_credentials_manager=get_client_credentials())
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

        items = response['items']
        offset = offset + len(items)
        all_tracks = all_tracks + items

    return  all_tracks


# Get playlist contents
def get_tracks(playlist_id):
    print("Starting get_tracks:")

    all_tracks = get_playlist_items(playlist_id)
    all_tracks = list(map(extract_track_info, all_tracks))

    print("Total song number: " + str(len(all_tracks)))
    print("get_tracks done.")
    return all_tracks


def prepare_spotify_query(song_name):
    return re.sub(" ", "%20", song_name)


def get_track_by_id(song_id):
    sp = spotipy.Spotify(client_credentials_manager=get_client_credentials())
    response = sp.track(track_id=song_id)

    return response


# Get Spotify track info about a track searching by song name
def get_track(song_name, artist):
    sp = spotipy.Spotify(client_credentials_manager=get_client_credentials())
    tracks = []
    offset = 0

    while True:
        response = sp.search(q="remaster%20track:" + prepare_spotify_query(song_name) + "%20artist:" + prepare_spotify_query(artist), offset=offset, type='track')
        if len(response['tracks']['items']) == 0:
            break

        offset = offset + len(tracks)
        tracks = tracks + response['tracks']['items']

    tracks.sort(reverse=True, key=lambda t: t['popularity'])
    items = list(map(extract_track_info_raw, tracks))
    return next(iter(items), None)


# Purge 'feat.' from song titles, since it impacts search results on Genius
def clean_title(title):
    ret = re.sub(".feat.*", "", title)
    return re.sub(".Remastered.*", "", ret)


# Get lyrics to songs using Genius API
def get_lyrics(track):
    print("Fetching lyrics")
    genius_token = vault_utils.get_secret("GeniusClientAccessToken")

    genius = Genius(access_token=genius_token, sleep_time=1, retries=5)
    artist = genius.search_artist(next(iter(track.artists or [])), max_songs=0)

    song_title = clean_title(track.name)
    song = genius.search_song(song_title, artist.name)

    if song is None:
        track.lyrics = ""
    else:
        track.lyrics = song.lyrics

    print("Lyrics fetched")
    return track
