import pandas as pd
import matplotlib.pyplot as plt

file_path = "finalcalcuation.txt"

with open(file_path, "r") as file:
    lines = file.readlines()

song_data = []
popularity_data = []
genre_data = []
data_section = None

for line in lines:
    line = line.strip()
    if line.startswith("Sum of Songs for Each Year:"):
        data_section = "songs"
        continue
    elif line.startswith("Average Popularity Score for Each Year:"):
        data_section = "popularity"
        continue
    elif line.startswith("Most Common Genre:") or line.startswith("Distribution of Songs by Artists:"):
        data_section = "genre"
        continue

    if data_section == "songs" and "Year:" in line:
        parts = line.replace("Year:", "").replace("Songs:", "").split(",")
        year, songs = int(parts[0].strip()), int(parts[1].strip())
        song_data.append((year, songs))
    elif data_section == "popularity" and "Year:" in line:
        parts = line.replace("Year:", "").replace("Average Popularity:", "").split(",")
        year, avg_popularity = int(parts[0].strip()), float(parts[1].strip())
        popularity_data.append((year, avg_popularity))
    elif data_section == "genre" and ":" in line:
        # Split the line only at the first colon
        parts = line.split(':', 1)
        genre = parts[0].strip().replace('Genre', '').strip()
        count_part = parts[1].strip().split()
        
        # Ensure first element of count_part is a number
        try:
            count = int(count_part[0])
            genre_data.append((genre, count))
        except ValueError:
            # Skip lines where count is not a valid integer
            continue

song_df = pd.DataFrame(song_data, columns=["Year", "Songs"])
popularity_df = pd.DataFrame(popularity_data, columns=["Year", "Average Popularity"])
genre_df = pd.DataFrame(genre_data, columns=["Genre", "Count"])

final_df = pd.merge(song_df, popularity_df, on="Year", how="outer")

print(final_df)
print(genre_df)

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

# Number of Songs per Genre
plt.figure(figsize=(10, 6))
plt.bar(genre_df["Genre"], genre_df["Count"], alpha=0.7)
plt.title("Number of Songs per Genre")
plt.xlabel("Genre")
plt.ylabel("Number of Songs")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("songs_per_genre.png")
plt.show()

# Genre Distribution Pie Chart
plt.figure(figsize=(10, 6))
plt.pie(genre_df["Count"], labels=genre_df["Genre"], autopct='%1.1f%%', startangle=140)
plt.title("Genre Distribution")
plt.tight_layout()
plt.savefig("genre_distribution.png")
plt.show()