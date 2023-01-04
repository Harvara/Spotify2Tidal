# Spotify to Tidal converter


This is a tool to automaticly converts spotify playlists to your tidal account.

It works either as a command line script, when you provide the playlist id as arg or it starts a local flask server that provides an endpoint that converts any given playlist

## Deployment Webserver
`
````docker compose up -d ````


## Usage as a script


```` 
pip3 install requirements.txt

python3 main.py -p <playlistid>

````

## Authorization

Currently the tidal login via an existing bearer token does not work. Therefore I build a workaround, which sends you an email with the login link for tidal.

The email is send via gmail, so you need an gmail api key, which you can get here [Gmail Docs](https://developers.google.com/gmail/api/auth/about-auth)

The tokens for the spotify app can be created on their [Developer Dashboard](https://developer.spotify.com/dashboard/login)