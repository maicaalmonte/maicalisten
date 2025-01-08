from flask import Flask, render_template_string
import spotipy
from datetime import datetime

app = Flask(__name__)

# Fixed Access Token (manually obtained)
access_token = 'YOUR_FIXED_ACCESS_TOKEN_HERE'

sp = spotipy.Spotify(auth=access_token)

@app.route('/')
def home():
    # Fetch the last 10 tracks
    recently_played = sp.current_user_recently_played(limit=10)

    # Collect the track information
    tracks_info = []
    for item in recently_played['items']:
        track = item['track']
        played_at = item['played_at']
        try:
            # Convert the timestamp to a readable format, adjusting for milliseconds and Z (UTC)
            formatted_time = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%B %d, %Y, %I:%M %p")
        except ValueError:
            # In case the format does not match, handle gracefully
            formatted_time = "Unknown time format"

        tracks_info.append({
            'name': track['name'],
            'artist': ', '.join(artist['name'] for artist in track['artists']),
            'album': track['album']['name'],
            'url': track['external_urls']['spotify'],
            'image': track['album']['images'][0]['url'] if track['album']['images'] else '',
            'played_at': formatted_time
        })

    # Render the HTML with minimal Spotify-like layout
    html_content = """
    <html>
    <head>
        <title>Recently Played Tracks</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #121212;
                color: white;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 350px;
                overflow-y: auto;
                padding: 10px;
                box-sizing: border-box;
            }
            .track {
                display: flex;
                align-items: center;
                background-color: #282828;
                border-radius: 8px;
                margin: 8px;
                padding: 8px;
                width: 100%;
                box-sizing: border-box;
            }
            .track img {
                width: 40px;
                height: 40px;
                border-radius: 5px;
                margin-right: 10px;
            }
            .track-info {
                display: flex;
                flex-direction: column;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .track-name {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .track-artist {
                font-size: 12px;
                margin-bottom: 4px;
                color: #b3b3b3;
            }
            .track-album {
                font-size: 10px;
                color: #b3b3b3;
            }
            .track-time {
                font-size: 10px;
                color: #b3b3b3;
                margin-top: 4px;
            }
            a {
                font-size: 10px;
                color: #1db954;
                text-decoration: none;
                margin-top: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Recently Played Tracks</h1>
            {% for track in tracks %}
                <div class="track">
                    <img src="{{ track.image }}" alt="{{ track.name }}">
                    <div class="track-info">
                        <div class="track-name">{{ track.name }}</div>
                        <div class="track-artist">{{ track.artist }}</div>
                        <div class="track-album">{{ track.album }}</div>
                        <div class="track-time">Played on: {{ track.played_at }}</div>
                        <a href="{{ track.url }}" target="_blank">Listen on Spotify</a>
                    </div>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """

    return render_template_string(html_content, tracks=tracks_info)

if __name__ == '__main__':
    app.run(debug=True, port=8888)
