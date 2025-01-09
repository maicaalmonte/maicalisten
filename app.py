from flask import Flask, request, redirect, render_template_string
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy
from datetime import datetime
from pytz import timezone

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
    scope="user-library-read user-read-recently-played user-top-read"
)

# Initialize a session to store the tokens
tokens = {}

def refresh_access_token(refresh_token):
    token_info = sp_oauth.refresh_access_token(refresh_token)
    return token_info['access_token'], token_info['refresh_token']

@app.route('/')
def home():
    # Redirect to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        # Get access token and refresh token
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']  # Store this for refreshing the token later

        # Save the tokens in the session
        tokens['access_token'] = access_token
        tokens['refresh_token'] = refresh_token

        return redirect('/top_tracks')  # Redirect to top tracks page after successful authorization

    else:
        return "Authorization failed."

@app.route('/top_tracks')
def top_tracks():
    # Ensure the user is authenticated and has an access token
    access_token = tokens.get('access_token')
    if access_token:
        sp = spotipy.Spotify(auth=access_token)

        # Fetch the top 5 tracks for the user
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')

        # Collect the track information
        tracks_info = []
        for track in top_tracks['items']:
            tracks_info.append({
                'name': track['name'],
                'artist': ', '.join(artist['name'] for artist in track['artists']),
                'album': track['album']['name'],
                'url': track['external_urls']['spotify'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else ''
            })

        # Render the HTML with minimal Spotify-like layout
        html_content = """
        <html>
        <head>
            <title>Top Tracks</title>
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
                <h1>Your Top Tracks</h1>
                {% for track in tracks %}
                    <div class="track">
                        <img src="{{ track.image }}" alt="{{ track.name }}">
                        <div class="track-info">
                            <div class="track-name">{{ track.name }}</div>
                            <div class="track-artist">{{ track.artist }}</div>
                            <div class="track-album">{{ track.album }}</div>
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
        return "You need to log in first."

# Example route to handle token refresh
@app.route('/refresh')
def refresh():
    refresh_token = tokens.get('refresh_token')
    if refresh_token:
        access_token, refresh_token = refresh_access_token(refresh_token)
        tokens['access_token'] = access_token
        tokens['refresh_token'] = refresh_token
        return "Access token refreshed!"
    else:
        return "No refresh token available."

if __name__ == '__main__':
    app.run(debug=True, port=8888)
