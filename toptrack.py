import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_top_tracks(offset=0, limit=25):
    client_id = '77fc84e558c245478be676b783ce0b73'
    client_secret = '249fc0faf1394289b14e520d19b92ac7'
    
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = "5ABHKGoOzxkaa28ttQV9sE"

    results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
    tracks = results['items']
    return tracks, sp


def get_artist_genres(artist_id, sp):
    artist = sp.artist(artist_id)
    return artist.get('genres', [])


def create_database():
    conn = sqlite3.connect('spotify_tracks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS TopTracks
                 (rank INTEGER PRIMARY KEY AUTOINCREMENT,
                  track_name TEXT,
                  artist TEXT,
                  album_name TEXT,
                  track_popularity INTEGER,
                  genres TEXT,
                  track_id TEXT UNIQUE)''')
    conn.commit()
    return conn, c


def insert_into_database(conn, c, data):
    try:
        c.execute("INSERT INTO TopTracks (track_name, artist, album_name, track_popularity, genres, track_id) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Track ID {data[-1]} already exists in the database. Skipping insertion.")


def print_and_save_tracks(tracks, sp, conn, c):
    for item in tracks:
        track = item['track']
        track_id = track['id']
        track_name = track['name']
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        track_popularity = track['popularity']

        # Get genres for the first artist (as an example)
        artist_id = track['artists'][0]['id']
        genres = get_artist_genres(artist_id, sp)
        genres = ', '.join(genres) if genres else 'Unknown'

        data = (track_name, artist_names, album_name, track_popularity, genres, track_id)
        print(f"Inserting track: {track_name}")
        insert_into_database(conn, c, data)


def get_current_track_count(conn, c):
    c.execute("SELECT COUNT(*) FROM TopTracks")
    count = c.fetchone()[0]
    return count


if __name__ == "__main__":
    conn, c = create_database()

    current_track_count = get_current_track_count(conn, c)
    offset = current_track_count
    limit = 25

    spotify_data, sp = get_spotify_top_tracks(offset=offset, limit=limit)
    print_and_save_tracks(spotify_data, sp, conn, c)
    
    conn.close()