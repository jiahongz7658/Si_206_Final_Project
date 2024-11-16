import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_top_tracks():
    client_id = '77fc84e558c245478be676b783ce0b73'
    client_secret = '249fc0faf1394289b14e520d19b92ac7'
    
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = "6UeSakyzhiEt4NB3UAd6NQ"   

    results = sp.playlist_tracks(playlist_id, limit=100)
    tracks = results['items']
    return tracks, sp

def get_artist_genres(artist_id, sp):
    artist = sp.artist(artist_id)
    return artist.get('genres', [])

def print_tracks(tracks, sp):
    for i, item in enumerate(tracks):
        track = item['track']
        track_id = track['id']
        track_name = track['name']
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        track_popularity = track['popularity']
        track_rank = i + 1  

        # Get genres for the first artist (as an example)
        artist_id = track['artists'][0]['id']
        genres = get_artist_genres(artist_id, sp)
        genres = ', '.join(genres) if genres else 'Unknown'

        print(f"Rank: {track_rank}")
        print(f"Track Name: {track_name}")
        print(f"Artists: {artist_names}")
        print(f"Album Name: {album_name}")
        print(f"Track Popularity: {track_popularity}")
        print(f"Genres: {genres}")
        print(f"Track ID: {track_id}")
        print()

if __name__ == "__main__":
    spotify_data, sp = get_spotify_top_tracks()
    print_tracks(spotify_data, sp)