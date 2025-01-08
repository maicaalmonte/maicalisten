from flask import Flask, request, redirect, render_template_string
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

SPOTIPY_CLIENT_ID = '6087621be5394ddf882a4d2bc72e50d6'
SPOTIPY_CLIENT_SECRET = '3e919d84ba064c7883dd2107568932b8'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-read-recently-played"
)

# Your existing token from the callback
access_token = 'BQCrd5iYK5I3V2zabGrU4zp-HcSujEeCTjeOHrO9UPG8ZCxcLL2dBTfu4q810StLK3EJsXt0ncrODbpBy9QhKbogvv-Ix8TmneZdzPjlOerbITObLIbe4_UPiN9Y0aUDhNM34nrpqMAGA2gBwWXiHsmiLorv0Qb8ZPTFDbIsZ8q2qRiRxmf58DJdlIm4SjL_aqxwfMlUHprc9dr0SL_FFyRVvQsgmv7Tcy6ljPw14ilBTIZ0lCofT9xqYNgF'

sp = spotipy.Spotify(auth=access_token)


@app.route('/')
def home():
    # Redirect to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        # Get access token
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        print(f"Access token: {access_token}")  # Log the token

        # Now use the access token to fetch the recently played tracks
        sp = spotipy.Spotify(auth=access_token)

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

    else:
        return "Authorization failed."


if __name__ == '__main__':
    app.run(debug=True, port=8888)
