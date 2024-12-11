import pandas as pd
import matplotlib.pyplot as plt
import re

file_path = "finalcalcuation.txt"

with open(file_path, "r") as file:
    lines = file.readlines()

song_data = []
popularity_data = []
genre_data = []
artist_data = []
data_section = None

for line in lines:
    line = line.strip()
    if line.startswith("Sum of Songs for Each Year:"):
        data_section = "songs"
        continue
    elif line.startswith("Average Popularity Score for Each Year:"):
        data_section = "popularity"
        continue
    elif line.startswith("Distribution of Genres:"):
        data_section = "genres"
        continue
    elif line.startswith("Distribution of Songs by Artists:"):
        data_section = "artists"
        continue
    elif line.startswith("Overall Average Popularity Score:") or line.startswith("Most Common Genre:"):
        data_section = None  # End data section

    if data_section == "songs" and "Year:" in line:
        parts = line.replace("Year:", "").replace("Songs:", "").split(",")
        year, songs = int(parts[0].strip()), int(parts[1].strip())
        song_data.append((year, songs))
    elif data_section == "popularity" and "Year:" in line:
        parts = line.replace("Year:", "").replace("Average Popularity:", "").split(",")
        year, avg_popularity = int(parts[0].strip()), float(parts[1].strip())
        popularity_data.append((year, avg_popularity))
    elif data_section == "genres" and "Genre:" in line:
        parts = line.replace("Genre:", "").replace("Songs:", "").split(",")
        genre, count = parts[0].strip(), int(parts[1].strip())
        genre_data.append((genre, count))
    elif data_section == "artists" and "Artist: " in line:
        match = re.match(r"Artist:\s*(.+?),\s*Songs:\s*(\d+)", line)
        if match:
            artist, songs = match.groups()
            artist_data.append((artist.strip(), int(songs.strip())))

song_df = pd.DataFrame(song_data, columns=["Year", "Songs"])
popularity_df = pd.DataFrame(popularity_data, columns=["Year", "Average Popularity"])
genre_df = pd.DataFrame(genre_data, columns=["Genre", "Count"])
artist_df = pd.DataFrame(artist_data, columns=["Artist", "Songs"])

final_df = pd.merge(song_df, popularity_df, on="Year")

print(final_df)
print(genre_df)
print(artist_df)

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

# Create a dictionary with the genre data
genre_data = {
    "Pop/HipHop": 121,
    "Other": 31,
    "Rock": 22,
    "Rap": 19
}

# Creating a pie chart for all genres' popularity
plt.figure(figsize=(8, 8))
plt.pie(
    genre_data.values(),
    labels=genre_data.keys(),
    autopct='%1.1f%%',
    startangle=140,
    colors=['red', 'blue', 'green', 'yellow']
)
plt.title("Genre Distribution Top 200")
plt.tight_layout()
plt.savefig("genre_distribution.png")
plt.show()

# Bar Chart of Top Artists
top_artists = artist_df.sort_values(by="Songs", ascending=False).head(10)

# Generate unique colors for each bar
colors = plt.cm.tab10(range(len(top_artists)))

plt.figure(figsize=(12, 8))  # Adjust the figure size for better readability
plt.bar(top_artists["Artist"], top_artists["Songs"], color=colors)
plt.title("Top 10 Artists by Number of Songs")
plt.xlabel("Artist")
plt.ylabel("Number of Songs")
plt.xticks(rotation=45, ha="right", fontsize=10)  # Rotate the x labels for better fit and increase font size
plt.tight_layout()  # Adjust layout
plt.savefig("top_10_artists_by_songs.png")
plt.show()