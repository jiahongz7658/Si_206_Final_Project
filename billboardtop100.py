import requests
import json

def fetch_billboard_data(api_key, chart_id='1'):
    url = f"https://api.chartmetric.com/api/playlist/{chart_id}/tracks"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    data = response.json()
    return data

def print_billboard_data(data):
    for track in data['obj']['tracks']:
        print(f"Rank: {track['position']}")
        print(f"Track Name: {track['name']}")
        print(f"Artist Name: {', '.join(artist['name'] for artist in track['artists'])}")
        print(f"Album Name: {track.get('album_name', 'N/A')}")
        print(f"Duration: {track['duration_ms']} ms")
        print(f"Isrc: {track['isrc']}")
        print()

if __name__ == "__main__":
    api_key = "YOUR_CHARTMETRIC_API_KEY"  # Replace with your Chartmetric API key
    chart_id = "64f87e1d62dfb03e5f199b8f"  # Replace with the specific chart's id
    billboard_data = fetch_billboard_data(api_key, chart_id)
    print_billboard_data(billboard_data)