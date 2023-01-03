import base64
import os

import requests



class Spotify:

    def __init__(self):
        self.token = os.getenv('SPOTIFY_ACCESS_TOKEN')
        self.refresh_token = os.getenv('SPOTIFY_REFRESH_TOKEN')
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.token_expired = True


    def token_valid(self):
        if self.token_expired:
            return False

        url = 'https://api.spotify.com/v1/me'
        user_headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=user_headers)

        return response.status_code == 200



    def connect(self):
        if not self.token_valid():
            self.renew_token()

    def renew_token(self):
        url = 'https://accounts.spotify.com/api/token'

        auth = self.client_id + ":" + self.client_secret
        message_bytes = auth.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)

        auth_headers = {
            "Authorization": "Basic " + base64_bytes.decode('ascii'),

        }

        data = {
            'grant_type': 'refresh_token',
            "refresh_token": self.refresh_token
        }


        token_data = requests.post(url,headers=auth_headers, data=data)

        self.token = token_data.json()['access_token']
        self.token_expired = False

    def get_playlist(self, playlist_id):
        self.connect()
        url = "https://api.spotify.com/v1/playlists/" + playlist_id
        user_headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

        playlist = requests.get(url,headers=user_headers)

        if playlist.status_code == 200:
            return playlist.json()
        return None

    def get_playlist_items(self, playlist_id):
        self.connect()
        next_page = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
        tracks = []

        while next_page:
            user_headers = {
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json"
            }

            response = requests.get(next_page,headers=user_headers)
            if response.status_code == 200:
                response_data = response.json()
                tracks.extend(response_data['items'])
                next_page = response_data['next']
            else:
                return None

        return tracks

