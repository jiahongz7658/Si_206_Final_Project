import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_top_tracks():
    client_id = '77fc84e558c245478be676b783ce0b73'
    client_secret = '249fc0faf1394289b14e520d19b92ac7'
    
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = "6UeSakyzhiEt4NB3UAd6NQ"   

    results = sp.playlist_tracks(playlist_id, limit=100)
    tracks = results['items']
    return tracks

def print_tracks(tracks):
    for i, item in enumerate(tracks):
        track = item['track']
        track_id = track['id']
        track_name = track['name']
        artist_name = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        track_popularity = track['popularity']
        track_rank = i + 1  

        print(f"Rank: {track_rank}")
        print(f"Track Name: {track_name}")
        print(f"Artist Name: {artist_name}")
        print(f"Album Name: {album_name}")
        print(f"Track Popularity: {track_popularity}")
        print(f"Track ID: {track_id}")
        print()
if __name__ == "__main__":
    spotify_data = get_spotify_top_tracks()
    print_tracks(spotify_data)