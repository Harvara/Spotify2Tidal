import getopt
import re
import sys

from flask import Flask, jsonify, Response
from dotenv import load_dotenv
from Spotify import Spotify
from Tidal import Tidal

load_dotenv()


def move_playlist(playlist_items, name, tidal):
    new_playlist = tidal.session.user.create_playlist(name, "Moved by script")
    size = playlist_items
    errors = 0
    for playlist_item in playlist_items:
        found_tracks = []
        track_data = playlist_item['track']
        query = track_data['name']
        for artist in track_data['artists']:
            query += " " + artist['name']

        tidal_search_result = tidal.search(query=query)
        if tidal_search_result:
            found_tracks = tidal_search_result['tracks']

        if len(found_tracks) > 0:
            if found_tracks[0].peak > 0.80:
                new_playlist.add([found_tracks[0].id])
            else:
                print("No sufficient match found for: " + query)
                print("Alternative: " + found_tracks[0].name + " by " + found_tracks[0].artist.name)
                errors += 1
        else:
            print("No match found for: " + query)
            errors += 1

    return [size, errors]


def option_playlist(playlist_id):
    spotify = Spotify()
    tidal = Tidal()
    tidal.connect()

    playlist = spotify.get_playlist(playlist_id)
    playlist_items = spotify.get_playlist_items(playlist_id)
    if playlist:
        playlist_name = playlist["name"]
        return move_playlist(playlist_items, playlist_name, tidal)

    return None


app = Flask(__name__)


@app.route('/copy-playlist/<playlistid>')
def copy(playlistid):
    if len(playlistid) == 22 and len(re.findall("^[-A-Za-z0-9+/]*={0,3}$", playlistid)) > 1:
        moved_items = option_playlist(playlistid)
        if moved_items and len(moved_items) == 2:
            return jsonify({
                'size of playlist': len(moved_items[0]),
                'items with errors': moved_items[1],
            })
    return Response("{'Message': 'Error converting the file'}", status=500)



@app.route('/')
def home():
    return jsonify({'Message': 'Welcome'})



if __name__ == '__main__':

    if len(sys.argv) > 1:
        argument_list = sys.argv[1:]
        options = 'hp:'
        long_options = ['help', 'user=', 'subreddit=']
        try:
            arguments, values = getopt.getopt(argument_list, options, long_options)

            if len(arguments) > 0:
                for currentArgument, currentValue in arguments:

                    if currentArgument in ("-h", "--Help"):
                        print("-playlist | -p  <playlistid>")

                    elif currentArgument in ("-p", "-playlist"):
                        option_playlist(currentValue.replace(" ", ""))

            else:
                print("Missing parameter")

        except getopt.error as err:
            print(str(err))

    else:
        print("No Parameter, running webserver")
        app.run()
