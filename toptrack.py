import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import musicbrainzngs
from collections import Counter

# Configure the MusicBrainz API
musicbrainzngs.set_useragent("SI 206 Final Project", "1.0", "jiahongz@umich.edu")

def create_database():
    conn = sqlite3.connect('music_repos_database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS TrackNames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS SpotifyTracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name_id INTEGER,
            artist_id INTEGER,
            album_name TEXT,
            track_popularity INTEGER,
            genre_id INTEGER,
            FOREIGN KEY (track_name_id) REFERENCES TrackNames(id),
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
        CREATE TABLE IF NOT EXISTS MusicBrainzYears (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            release_year INTEGER UNIQUE
        )
    ''')

    # Create the final consolidated table
    c.execute('''
        CREATE TABLE IF NOT EXISTS FinalTracks (
            id INTEGER PRIMARY KEY,  -- Same as SpotifyTracks.id
            track_name_id INTEGER,
            artist_id INTEGER,
            track_popularity INTEGER,
            genre_id INTEGER,
            release_year_id INTEGER,
            FOREIGN KEY (track_name_id) REFERENCES TrackNames(id),
            FOREIGN KEY (artist_id) REFERENCES Artists(id),
            FOREIGN KEY (genre_id) REFERENCES Genres(id),
            FOREIGN KEY (release_year_id) REFERENCES MusicBrainzYears(id)
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

def get_track_name_id(track_name, c, conn):
    c.execute('SELECT id FROM TrackNames WHERE track_name = ?', (track_name,))
    result = c.fetchone()

    if result:
        return result[0]
    else:
        c.execute('INSERT INTO TrackNames (track_name) VALUES (?)', (track_name,))
        conn.commit()
        return c.lastrowid

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
        
        for genre in genre_list:
            category = map_genre_to_category(genre)
            genre_id = get_genre_id(category, c, conn)
            categories.append(genre_id)

        return categories
    except Exception as e:
        print(f"Error fetching genres for artist {artist_name}: {e}")
        return []

def fetch_musicbrainz_release_year(track_name, artist_name):
    try:
        print(f"Searching MusicBrainz for: {track_name} by {artist_name}")
        results = musicbrainzngs.search_recordings(recording=track_name, artist=artist_name, limit=1)
        if 'recording-list' in results:
            recording = results['recording-list'][0]
            recording_id = recording['id']

            recording_details = musicbrainzngs.get_recording_by_id(recording_id, includes=['releases'])
            release_list = recording_details['recording'].get('release-list', [])
            release_year = None

            if release_list:
                release_dates = [release.get('date') for release in release_list if release.get('date')]
                if release_dates:
                    release_year = min(release_dates)[:4]  # Extract the year part
                print(f"Release dates found: {release_dates}, earliest year: {release_year}")

            return release_year
    except Exception as e:
        print(f"Error fetching MusicBrainz data for {track_name} by {artist_name}: {e}.")
    return None

def get_release_year_id(release_year, c, conn):
    c.execute('SELECT id FROM MusicBrainzYears WHERE release_year = ?', (release_year,))
    result = c.fetchone()

    if result:
        return result[0]
    else:
        c.execute('INSERT INTO MusicBrainzYears (release_year) VALUES (?)', (release_year,))
        conn.commit()
        return c.lastrowid

def record_exists(c, table, column, value):
    c.execute(f'SELECT COUNT(1) FROM {table} WHERE {column} = ?', (value,))
    return c.fetchone()[0] > 0

def insert_into_database(conn, c, table_name, data):
    try:
        if table_name == 'SpotifyTracks':
            c.execute('''
            INSERT INTO SpotifyTracks (track_name_id, artist_id, album_name, track_popularity, genre_id)
            VALUES (?, ?, ?, ?, ?)
            ''', data)
        elif table_name == 'MusicBrainzYears':
            c.execute('''
            INSERT INTO MusicBrainzYears (release_year)
            VALUES (?)
            ''', data)
        elif table_name == 'FinalTracks':
            c.execute('''
            INSERT INTO FinalTracks (id, track_name_id, artist_id, track_popularity, genre_id, release_year_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', data)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}. Skipping insertion for data {data}.")

def print_and_save_tracks(tracks, sp, conn, c):
    if not tracks:
        print("No tracks to process.")
        return 0

    spotify_tracks_inserted = 0
    processed_track_names = []

    for item in tracks:
        track = item['track']
        track_name = track['name']
        processed_track_names.append(track_name)
        album_name = track['album']['name']
        track_popularity = track['popularity']
        track_artists = track['artists']
        artist_id = None
        genre_id = None
        release_year = None
        release_year_id = None

        if spotify_tracks_inserted >= 25:
            print(f"Inserted 25 tracks this run.")
            break

        try:
            # Only fetch the first artist
            if track_artists:
                artist = track_artists[0]
                artist_name = artist['name']
                artist_id = get_artist_id(artist_name, c, conn)

                genres = get_artist_genres(artist['id'], artist_name, sp, c, conn)
                genre_id = Counter(genres).most_common(1)[0][0] if genres else None  # Get the most frequent genre ID

            release_year = fetch_musicbrainz_release_year(track_name, artist_name)
            if release_year:
                release_year_id = get_release_year_id(release_year, c, conn)

            # Get track name ID
            track_name_id = get_track_name_id(track_name, c, conn)

            # Check if this track is already processed
            if not record_exists(c, 'SpotifyTracks', 'track_name_id', track_name_id):
                spotify_data = (track_name_id, artist_id, album_name, track_popularity, genre_id)
                print(f"Inserting track: {track_name} into SpotifyTracks with track name ID {track_name_id}")
                insert_into_database(conn, c, 'SpotifyTracks', spotify_data)
                spotify_tracks_inserted += 1

                # Insert into FinalTracks only if SpotifyTracks insertion was successful
                c.execute('SELECT id FROM SpotifyTracks WHERE track_name_id = ?', (track_name_id,))
                spotify_internal_id = c.fetchone()[0]

                final_data = (spotify_internal_id, track_name_id, artist_id, track_popularity, genre_id, release_year_id)
                print(f"Inserting track: {track_name} into FinalTracks with id {spotify_internal_id}")
                insert_into_database(conn, c, 'FinalTracks', final_data)

        except Exception as e:
            print(f"Error processing track {track_name}: {e}")

    print(f"Processed tracks in this run: {processed_track_names}")
    print(f"Total tracks inserted this run: {spotify_tracks_inserted}")
    return spotify_tracks_inserted

if __name__ == "__main__":
    conn, c = create_database()

    limit_per_run = 25
    total_final_tracks_inserted = c.execute('SELECT COUNT(*) FROM FinalTracks').fetchone()[0]

    if total_final_tracks_inserted < 200:
        offset = total_final_tracks_inserted
        spotify_data, sp = get_spotify_top_tracks(offset=offset, limit=limit_per_run)
        spotify_tracks_inserted = print_and_save_tracks(spotify_data, sp, conn, c)
        total_final_tracks_inserted += spotify_tracks_inserted
        print(f"Total final tracks inserted after this run: {total_final_tracks_inserted}")
    else:
        print("200 tracks have already been inserted.")

    conn.close()

    # Select and join data from final table for verification
    conn, c = create_database()
    c.execute('''
        SELECT 
            FT.id, 
            TN.track_name, 
            FT.artist_id, 
            FT.track_popularity, 
            FT.genre_id, 
            FT.release_year_id 
        FROM 
            FinalTracks FT 
        JOIN 
            TrackNames TN 
        ON 
            FT.track_name_id = TN.id
    ''')
    results = c.fetchall()

    # Print results for verification
    for row in results:
        print(row)

    conn.close()