from dotenv import load_dotenv
from Spotify import Spotify
from Tidal import Tidal

load_dotenv()


def move_playlist(playlist, name, tidal):
    new_playlist = tidal.session.user.create_playlist(name, "Moved by script")
    for playlist_item in playlist['tracks']['items']:
        track_data = playlist_item['track']
        query = track_data['name']
        for artist in track_data['artists']:
            query += " " + artist['name']

        found_tracks = tidal.search(query=query)['tracks']

        if len(found_tracks) > 0:
            if found_tracks[0].peak > 0.99:
                new_playlist.add(found_tracks[0].id)
            print("No sufficient match found for: " + query)
            print("Alternative: " + found_tracks[0].name +  " by " + found_tracks[0].artist.name)
        else:
            print("No match found for: " + query)





spotify = Spotify()
tidal = Tidal()
tidal.connect()

playlist_id = '3cEYpjA9oz9GiPac4AsH4n'
playlist_name = 'Sample Playlist'
playlist = spotify.get_playlist(playlist_id)
move_playlist(playlist, playlist_name, tidal)
