import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import musicbrainzngs
from collections import Counter

# Configure MusicBrainz API
musicbrainzngs.set_useragent("SI 206 Final Project", "1.0", "jiahongz@umich.edu")

def create_database():
    conn = sqlite3.connect('music_repos_database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS SpotifyTracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT UNIQUE,
            artist_id INTEGER,
            album_name TEXT,
            track_popularity INTEGER,
            genre_id INTEGER,
            FOREIGN KEY (artist_id) REFERENCES Artists(id),
            FOREIGN KEY (genre_id) REFERENCES Genres(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS MusicBrainzTracks (
            spotify_track_id INTEGER PRIMARY KEY,
            release_date TEXT,
            FOREIGN KEY (spotify_track_id) REFERENCES SpotifyTracks(id)
        )
    ''')

    conn.commit()
    return conn, c

def get_spotify_top_tracks(offset=0, limit=25):
    client_id = '77fc84e558c245478be676b783ce0b73'
    client_secret = '249fc0faf1394289b14e520d19b92ac7'
    
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = "2YRe7HRKNRvXdJBp9nXFza"  # Example playlist ID

    try:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        return results['items'], sp
    except Exception as e:
        print(f"Error fetching Spotify tracks: {e}")
        return [], sp

def get_artist_id(artist_name, c, conn):
    c.execute('SELECT id FROM Artists WHERE artist_name = ?', (artist_name,))
    result = c.fetchone()

    if result:
        return result[0]
    else:
        c.execute('INSERT INTO Artists (artist_name) VALUES (?)', (artist_name,))
        conn.commit()
        return c.lastrowid

def get_genre_id(genre_name, c, conn):
    c.execute('SELECT id FROM Genres WHERE genre = ?', (genre_name,))
    result = c.fetchone()

    if result:
        return result[0]
    else:
        c.execute('INSERT INTO Genres (genre) VALUES (?)', (genre_name,))
        conn.commit()
        return c.lastrowid

# Function to map genres to specific categories
def map_genre_to_category(genre):
    genre = genre.lower()
    if any(g in genre for g in ['pop', 'hip hop', 'hiphop']):
        return 'pop/hiphop'
    elif 'r&b' in genre or 'rnb' in genre:
        return 'r&b'
    elif 'rock' in genre:
        return 'rock'
    elif 'funk' in genre:
        return 'funk'
    elif 'rap' in genre:
        return 'rap'
    else:
        return 'other'

def get_artist_genres(artist_id, artist_name, sp, c, conn):
    try:
        categories = []
        artist = sp.artist(artist_id)
        genre_list = artist.get('genres', [])
        
        # Map genres to categories
        for genre in genre_list:
            category = map_genre_to_category(genre)
            genre_id = get_genre_id(category, c, conn)
            categories.append(genre_id)

        return categories  # Return list of category IDs
    except Exception as e:
        print(f"Error fetching genres for artist {artist_name}: {e}")
        return []

def fetch_musicbrainz_release_date(track_name, artist_name):
    try:
        print(f"Searching MusicBrainz for: {track_name} by {artist_name}")
        results = musicbrainzngs.search_recordings(recording=track_name, artist=artist_name, limit=1)
        if 'recording-list' in results:
            recording = results['recording-list'][0]
            recording_id = recording['id']

            # Fetch recording details including releases to get the release date
            recording_details = musicbrainzngs.get_recording_by_id(recording_id, includes=['releases'])
            release_list = recording_details['recording'].get('release-list', [])
            release_date = None

            if release_list:
                release_dates = [release.get('date') for release in release_list if release.get('date')]
                if release_dates:
                    release_date = min(release_dates)
                print(f"Release dates found: {release_dates}, earliest: {release_date}")

            return (release_date,)
    except Exception as e:
        print(f"Error fetching MusicBrainz data for {track_name} by {artist_name}: {e}.")
    return (None,)

def record_exists(c, table, column, value):
    c.execute(f'SELECT COUNT(1) FROM {table} WHERE {column} = ?', (value,))
    return c.fetchone()[0] > 0

def insert_into_database(conn, c, table_name, data):
    try:
        if table_name == 'SpotifyTracks':
            c.execute('''
            INSERT INTO SpotifyTracks (track_name, artist_id, album_name, track_popularity, genre_id)
            VALUES (?, ?, ?, ?, ?)
            ''', data)
        elif table_name == 'MusicBrainzTracks':
            c.execute('''
            INSERT INTO MusicBrainzTracks (spotify_track_id, release_date)
            VALUES (?, ?)
            ''', data)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}. Skipping insertion for data {data}.")

def print_and_save_tracks(tracks, sp, conn, c, spotify_tracks_count, musicbrainz_tracks_count):
    if not tracks:
        print("No tracks to process.")
        return

    spotify_tracks_inserted = 0
    musicbrainz_tracks_inserted = 0

    for item in tracks:
        if spotify_tracks_count + spotify_tracks_inserted >= 200 and musicbrainz_tracks_count + musicbrainz_tracks_inserted >= 200:
            break

        try:
            track = item['track']
            track_name = track['name']
            artist_ids = []
            album_name = track['album']['name']
            track_popularity = track['popularity']
            track_artists = track['artists']

            for artist in track['artists']:
                artist_name = artist['name']
                artist_id = get_artist_id(artist_name, c, conn)
                artist_ids.append(artist_id)

                genres = get_artist_genres(artist['id'], artist_name, sp, c, conn)
                if not genres:
                    genre_id = None
                else:
                    genre_id = Counter(genres).most_common(1)[0][0]  # Get the most frequent genre ID

                spotify_data = (track_name, artist_id, album_name, track_popularity, genre_id)
                if not record_exists(c, 'SpotifyTracks', 'track_name', track_name):
                    print(f"Inserting track: {track_name} into SpotifyTracks")
                    insert_into_database(conn, c, 'SpotifyTracks', spotify_data)
                    spotify_tracks_inserted += 1

                    c.execute('SELECT id FROM SpotifyTracks WHERE track_name = ?', (track_name,))
                    spotify_internal_id = c.fetchone()[0]

                    if not record_exists(c, 'MusicBrainzTracks', 'spotify_track_id', spotify_internal_id):
                        musicbrainz_data = fetch_musicbrainz_release_date(track_name, artist_name)
                        release_data = (spotify_internal_id, *musicbrainz_data)
                        print(f"Inserting release date for track: {track_name} into MusicBrainzTracks")
                        insert_into_database(conn, c, 'MusicBrainzTracks', release_data)
                        musicbrainz_tracks_inserted += 1

        except Exception as e:
            print(f"Error processing track {track_name}: {e}")

    return spotify_tracks_inserted, musicbrainz_tracks_inserted

if __name__ == "__main__":
    conn, c = create_database()

    total_tracks_to_fetch = 200
    limit_per_run = 25
    total_spotify_tracks_inserted = c.execute('SELECT COUNT(*) FROM SpotifyTracks').fetchone()[0]
    total_musicbrainz_tracks_inserted = c.execute('SELECT COUNT(*) FROM MusicBrainzTracks').fetchone()[0]

    while total_spotify_tracks_inserted < total_tracks_to_fetch or total_musicbrainz_tracks_inserted < total_tracks_to_fetch:
        offset = max(total_spotify_tracks_inserted, total_musicbrainz_tracks_inserted)
        spotify_data, sp = get_spotify_top_tracks(offset=offset, limit=limit_per_run)
        spotify_tracks_inserted, musicbrainz_tracks_inserted = print_and_save_tracks(spotify_data, sp, conn, c, total_spotify_tracks_inserted, total_musicbrainz_tracks_inserted)

        total_spotify_tracks_inserted += spotify_tracks_inserted
        total_musicbrainz_tracks_inserted += musicbrainz_tracks_inserted

    conn.close()