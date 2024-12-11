import sqlite3
from collections import Counter

def music_calculation():
    conn = sqlite3.connect('music_repos_database.db')
    c = conn.cursor()

    with open("finalcalcuation.txt", "w") as file:
        # 1. Sum of songs for each year in MusicBrainzYears
        c.execute('''
            SELECT MY.release_year, COUNT(*) 
            FROM FinalTracks FT
            JOIN MusicBrainzYears MY ON FT.release_year_id = MY.id
            GROUP BY MY.release_year
        ''')
        year_counts = c.fetchall()
        file.write("Sum of Songs for Each Year:\n")
        for year, count in year_counts:
            file.write(f"Year: {year}, Songs: {count}\n")
        file.write("\n")

        # 2. Average popularity score for each year
        c.execute('''
            SELECT MY.release_year, AVG(FT.track_popularity)
            FROM FinalTracks FT
            JOIN MusicBrainzYears MY ON FT.release_year_id = MY.id
            GROUP BY MY.release_year
        ''')
        year_popularity_averages = c.fetchall()
        file.write("Average Popularity Score for Each Year:\n")
        for year, avg_popularity in year_popularity_averages:
            file.write(f"Year: {year}, Average Popularity: {avg_popularity:.2f}\n")
        file.write("\n")

        # 3. Overall average popularity score
        c.execute('''
            SELECT AVG(track_popularity) FROM FinalTracks
        ''')
        overall_avg_popularity = c.fetchone()[0]
        file.write(f"Overall Average Popularity Score: {overall_avg_popularity:.2f}\n")
        file.write("\n")

        # 4. Most common genre
        c.execute('''
            SELECT genre, COUNT(genre_id) as genre_count
            FROM FinalTracks FT
            JOIN Genres G ON FT.genre_id = G.id
            GROUP BY genre_id
            ORDER BY genre_count DESC
            LIMIT 1
        ''')
        most_common_genre = c.fetchone()
        file.write(f"Most Common Genre: {most_common_genre[0]} with {most_common_genre[1]} occurrences\n")
        file.write("\n")

        # 5. Distribution of songs by artists
        c.execute('''
            SELECT A.artist_name, COUNT(FT.artist_id) 
            FROM FinalTracks FT
            JOIN Artists A ON FT.artist_id = A.id
            GROUP BY FT.artist_id
            ORDER BY COUNT(FT.artist_id) DESC
        ''')
        artist_distribution = c.fetchall()
        file.write("Distribution of Songs by Artists:\n")
        for artist, count in artist_distribution:
            file.write(f"Artist: {artist}, Songs: {count}\n")
        file.write("\n")

        # 6. Distribution of genres
        c.execute('''
            SELECT G.genre, COUNT(FT.genre_id) as genre_count
            FROM FinalTracks FT
            JOIN Genres G ON FT.genre_id = G.id
            GROUP BY FT.genre_id
            ORDER BY genre_count DESC
        ''')
        genre_distribution = c.fetchall()
        file.write("Distribution of Genres:\n")
        for genre, count in genre_distribution:
            file.write(f"Genre: {genre}, Songs: {count}\n")
        file.write("\n")

    conn.close()

if __name__ == '__main__':
    music_calculation()
    print("Statistics generated and saved to finalcalcuation.txt")
