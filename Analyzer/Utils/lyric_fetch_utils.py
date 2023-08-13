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


def prepare_spotify_query(song_name):
    return re.sub(" ", "%20", song_name)


# Get Spotify track info about a track searching by song name
def get_track(song_name, artist):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
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
def purge_feat_from_title(title):
    return re.sub(".feat.*", "", title)


# Get lyrics to songs using Genius API
def get_lyrics(track):
    print("Fetching lyrics")
    genius_token = vault_utils.get_secret("GeniusClientAccessToken")

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
