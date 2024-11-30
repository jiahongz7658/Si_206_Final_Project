import musicbrainzngs

# Set up the user agent
musicbrainzngs.set_useragent(
    "SI 206 Final Project",  # Replace with your application name
    "1.0",          # Replace with your application version
    "jiahongz@umich.edu"  # Replace with your contact information
)

def search_artist(artist_name):
    try:
        # Search for the artist by name
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        if result['artist-list']:
            # Get the first artist in the list
            artist = result['artist-list'][0]
            # Print artist details
            print(f"Artist Name: {artist['name']}")
            print(f"Country: {artist['country'] if 'country' in artist else 'Unknown'}")
            print(f"Disambiguation: {artist['disambiguation'] if 'disambiguation' in artist else 'None'}")
            print(f"Type: {artist['type'] if 'type' in artist else 'Unknown'}")
            print(f"Life Span: {artist['life-span']['begin']} - {artist['life-span']['end'] if 'end' in artist['life-span'] else 'Present'}")
        else:
            print("No artist found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    search_artist("The Beatles")