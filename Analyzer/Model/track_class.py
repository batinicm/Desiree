class Track:
    def __init__(self, spotify_id, name, artists, lyrics=None):
        self.spotify_id = spotify_id
        self.name = name
        self.artists = artists
        self.lyrics = lyrics

    def to_dict(track):
        return {
            "SpotifyId": track.spotify_id,
            "Name": track.name,
            "Artists": track.artists,
            "Lyrics": track.lyrics
        }
