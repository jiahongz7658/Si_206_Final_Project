import pandas as pd
import matplotlib.pyplot as plt

file_path = "finalcalcuation.txt"

with open(file_path, "r") as file:
    lines = file.readlines()

song_data = []
popularity_data = []
data_section = None

for line in lines:
    line = line.strip()
    if line.startswith("Sum of Songs for Each Year:"):
        data_section = "songs"
        continue
    elif line.startswith("Average Popularity Score for Each Year:"):
        data_section = "popularity"
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

song_df = pd.DataFrame(song_data, columns=["Year", "Songs"])
popularity_df = pd.DataFrame(popularity_data, columns=["Year", "Average Popularity"])

final_df = pd.merge(song_df, popularity_df, on="Year")

print(final_df)

# song count per year
plt.figure(figsize=(10, 6))
plt.bar(final_df["Year"], final_df["Songs"], alpha=0.7)
plt.title("Number of Songs Released Each Year")
plt.xlabel("Year")
plt.ylabel("Number of Songs")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("songs_per_year.png")
plt.show()

# average popularity score per year
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

# scatter plot of Songs vs. Average Popularity

plt.figure(figsize=(10, 6))
plt.scatter(final_df["Songs"], final_df["Average Popularity"], color='g', alpha=0.7)
plt.title("Songs vs. Average Popularity")
plt.xlabel("Number of Songs")
plt.ylabel("Average Popularity")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("songs_vs_average_popularity.png")
plt.show()

# trend line for Average Popularity over Years
plt.figure(figsize=(10, 6))
plt.plot(final_df["Year"], final_df["Average Popularity"], marker='o', linestyle='-', color='c', label="Trend")
plt.fill_between(final_df["Year"], final_df["Average Popularity"], color='c', alpha=0.1)
plt.title("Trend of Average Popularity Over the Years")
plt.xlabel("Year")
plt.ylabel("Average Popularity")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("popularity_trend_over_years.png")
plt.show()