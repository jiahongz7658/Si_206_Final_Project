import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import time

# Function to create tables in SQLite
def create_tables(conn):
    with conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS spotify_tracks (
            id TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            popularity INTEGER,
            genres TEXT,
            spotify_uri TEXT
        )
        ''')

# Fetch Spotify top tracks
def get_spotify_top_tracks(limit=25):
    client_id = '77fc84e558c245478be676b783ce0b73'
    client_secret = '249fc0faf1394289b14e520d19b92ac7'
    
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = "6UeSakyzhiEt4NB3UAd6NQ"  # Corrected Spotify Global Top 50 playlist ID

    results = sp.playlist_tracks(playlist_id, limit=limit)
    tracks = results['items']
    return tracks, sp

# Fetch artist genres
def get_artist_genres(artist_id, sp):
    artist = sp.artist(artist_id)
    return artist.get('genres', [])

# Save Spotify tracks to database
def save_spotify_tracks_to_db(tracks, sp):
    conn = sqlite3.connect('music_data.db')
    with conn:
        for item in tracks:
            track = item['track']
            track_id = track['id']
            track_name = track['name']
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            album_name = track['album']['name']
            track_popularity = track['popularity']
            spotify_uri = track['uri']

            artist_id = track['artists'][0]['id']
            genres = get_artist_genres(artist_id, sp)
            genres = ', '.join(genres) if genres else 'Unknown'

            conn.execute('''
            INSERT OR REPLACE INTO spotify_tracks (id, name, artist, album, popularity, genres, spotify_uri)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (track_id, track_name, artist_names, album_name, track_popularity, genres, spotify_uri))

    conn.close()

if __name__ == "__main__":
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('music_data.db')
    
    # 1. Create tables
    create_tables(conn)
    conn.close()

    # 2. Fetch and store Spotify data in batches of 25 items per run
    limit = 25
    runs_needed = 4  # Number of runs needed to reach 100 items (25 items per run * 4 runs = 100 items)

    for run in range(runs_needed):
        spotify_data, sp = get_spotify_top_tracks(limit)
        save_spotify_tracks_to_db(spotify_data, sp)
        print(f"Run {run+1} complete. Saved {limit} tracks.")
        time.sleep(1)  # Optional: Add delay to avoid API rate limits or other timing issues

    print("Data collection complete. At least 100 Spotify tracks saved to the database.")