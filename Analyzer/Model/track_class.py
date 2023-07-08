class Track:
    def __init__(self, spotify_id, name, artists, lyrics = None):
        self.spotify_id = spotify_id
        self.name = name
        self.artists = artists
        self.lyrics = lyrics
