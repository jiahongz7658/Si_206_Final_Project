import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def fetch_data_from_database():
    conn = sqlite3.connect('music_repos_database.db')
    c = conn.cursor()

    # Sum of songs for each year
    c.execute('''
        SELECT MY.release_year, COUNT(*) 
        FROM FinalTracks FT
        JOIN MusicBrainzYears MY ON FT.release_year_id = MY.id
        GROUP BY MY.release_year
        ORDER BY MY.release_year
    ''')
    year_counts = c.fetchall()

    # Average popularity score for each year
    c.execute('''
        SELECT MY.release_year, AVG(FT.track_popularity)
        FROM FinalTracks FT
        JOIN MusicBrainzYears MY ON FT.release_year_id = MY.id
        GROUP BY MY.release_year
        ORDER BY MY.release_year
    ''')
    year_popularity_averages = c.fetchall()

    # Genre distribution
    c.execute('''
        SELECT G.genre, COUNT(FT.genre_id) as genre_count
        FROM FinalTracks FT
        JOIN Genres G ON FT.genre_id = G.id
        GROUP BY G.genre
        ORDER BY genre_count DESC
    ''')
    genre_distribution = c.fetchall()

    # Distribution of songs by artists
    c.execute('''
        SELECT A.artist_name, COUNT(FT.artist_id)
        FROM FinalTracks FT
        JOIN Artists A ON FT.artist_id = A.id
        GROUP BY FT.artist_id
        ORDER BY COUNT(FT.artist_id) DESC
    ''')
    artist_distribution = c.fetchall()

    conn.close()

    return year_counts, year_popularity_averages, genre_distribution, artist_distribution

def classify_genre(genre):
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

def generate_visualizations(year_counts, year_popularity_averages, genre_distribution, artist_distribution):
    # Create DataFrames
    song_df = pd.DataFrame(year_counts, columns=["Year", "Songs"])
    popularity_df = pd.DataFrame(year_popularity_averages, columns=["Year", "Average Popularity"])
    artist_df = pd.DataFrame(artist_distribution, columns=["Artist", "Songs"])

    final_df = pd.merge(song_df, popularity_df, on="Year")

    print("Final DataFrame for Songs and Popularity:\n", final_df)
    print("Artist Distribution:\n", artist_df)

    # Song count per year
    plt.figure(figsize=(10, 6))
    plt.bar(final_df["Year"], final_df["Songs"], alpha=0.7)
    plt.title("Number of Songs Released Each Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Songs")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("songs_per_year.png")
    plt.show()

    # Average popularity score per year
    plt.figure(figsize=(10, 6))
    plt.plot(final_df["Year"], final_df["Average Popularity"], marker='o', linestyle='-', color='b')
    plt.title("Average Popularity Score Per Year")
    plt.xlabel("Year")
    plt.ylabel("Average Popularity")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("average_popularity_per_year.png")
    plt.show()

    # Consolidate Genre Data
    consolidated_genres = {}
    for genre, count in genre_distribution:
        classified_genre = classify_genre(genre)
        if classified_genre in consolidated_genres:
            consolidated_genres[classified_genre] += count
        else:
            consolidated_genres[classified_genre] = count

    genre_df = pd.DataFrame(list(consolidated_genres.items()), columns=['Genre', 'Count'])

    print("Genre Distribution:\n", genre_df)

    # Genre Distribution Pie Chart
    plt.figure(figsize=(10, 6))
    plt.pie(genre_df["Count"], labels=genre_df["Genre"], autopct='%1.1f%%', startangle=140)
    plt.title("Genre Distribution")
    plt.tight_layout()
    plt.savefig("genre_distribution.png")
    plt.show()

    # Bar Chart of Top Artists with Unique Colors
    top_artists = artist_df.sort_values(by="Songs", ascending=False).head(10)
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_artists)))  # Generate unique colors

    plt.figure(figsize=(12, 8))  # Adjust the figure size for better readability
    plt.bar(top_artists["Artist"], top_artists["Songs"], color=colors)
    plt.title("Top 10 Artists by Number of Songs")
    plt.xlabel("Artist")
    plt.ylabel("Number of Songs")
    plt.xticks(rotation=45, ha="right", fontsize=10)  # Rotate the x labels for better fit and increase font size
    plt.tight_layout()  # Adjust layout
    plt.savefig("top_10_artists_by_songs.png")
    plt.show()

if __name__ == "__main__":
    year_counts, year_popularity_averages, genre_distribution, artist_distribution = fetch_data_from_database()
    generate_visualizations(year_counts, year_popularity_averages, genre_distribution, artist_distribution)