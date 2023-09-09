import getopt
import re
import sys

from flask import Flask, jsonify, Response
from dotenv import load_dotenv
from Spotify import Spotify
from Tidal import Tidal
from fuzzywuzzy import fuzz

SIMILARITY = 0.70

load_dotenv()


def playlist_already_exists(tidal, playlist_id):
    playlists = tidal.session.user.playlists()
    for playlist in playlists:
        if playlist.description == playlist_id:
            return playlist

    return None


def create_tracklist_from_playlist(tidal_playlist):
    tracks = []
    for items in tidal_playlist.items():
        tracks.append(items.full_name)
    return tracks


def item_already_exists(spotify_track_name, tidal_tracks):
    for tidal_track_name in tidal_tracks:
        similarity = fuzz.token_sort_ratio(spotify_track_name, tidal_track_name)
        if similarity/100 >= SIMILARITY:
            return True

    return False


def update_playlist(playlist_items, tidal_playlist, tidal):
    tidal_tracks = create_tracklist_from_playlist(tidal_playlist)
    successful = 0
    errors = 0
    for playlist_item in playlist_items:
        if not item_already_exists(playlist_item["track"]["name"], tidal_tracks):
            tidal_id = get_tidal_id(playlist_item["track"], tidal)
            if tidal_id:
                tidal_playlist.add([tidal_id])
                successful += 1
            else:
                errors += 1
    return successful, errors


def create_search_query(track_data):
    query = track_data['name']
    for artist in track_data['artists']:
        query += " " + artist['name']

    return query


def get_tidal_id(track, tidal):
    found_tracks = []
    query = create_search_query(track)

    tidal_search_result = tidal.search(query=query)
    if tidal_search_result:
        found_tracks = tidal_search_result['tracks']

    if len(found_tracks) > 0:
        if found_tracks[0].peak > SIMILARITY:
            return found_tracks[0].id
        else:
            print("No sufficient match found for: " + query)
            print("Alternative: " + found_tracks[0].name + " by " + found_tracks[0].artist.name)
            return None
    else:
        print("No match found for: " + query)
        return None


def move_playlist(playlist_items, name, spotify_id, tidal):
    new_playlist = tidal.session.user.create_playlist(name, spotify_id)
    errors = 0
    successful = 0
    for playlist_item in playlist_items:
        tidal_id = get_tidal_id(playlist_item['track'], tidal)
        if tidal_id:
            new_playlist.add([tidal_id])
            successful += 1
        else:
            errors += 1
    return successful, errors


def option_playlist(playlist_id):
    spotify = Spotify()
    tidal = Tidal()
    tidal.connect()

    spotify_playlist = spotify.get_playlist(playlist_id)
    playlist_items = spotify.get_playlist_items(playlist_id)
    if spotify_playlist:
        playlist_name = spotify_playlist["name"]
        tidal_playlist = playlist_already_exists(tidal, playlist_id)
        if tidal_playlist:
            return update_playlist(playlist_items, tidal_playlist, tidal)
        return move_playlist(playlist_items, playlist_name, playlist_id, tidal)

    return None


app = Flask(__name__)


@app.route('/copy-playlist/<playlist_id>')
def copy(playlist_id):
    if len(playlist_id) == 22 and len(re.findall("^[-A-Za-z0-9+/]*={0,3}$", playlist_id)) == 1:
        copy_playlist_result = option_playlist(playlist_id)
        if copy_playlist_result and len(copy_playlist_result) == 2:
            return jsonify({
                'copied items': copy_playlist_result[0],
                'items with errors': copy_playlist_result[1],
            })
    return Response("{'Message': 'Error converting the file'}", status=500)


@app.route('/')
def home():
    return jsonify({'Message': 'Welcome'})


if __name__ == '__main__':

    if len(sys.argv) > 1:
        argument_list = sys.argv[1:]
        options = 'hp:'
        long_options = ['help', 'playlist=']
        try:
            arguments, values = getopt.getopt(argument_list, options, long_options)

            if len(arguments) > 0:
                for currentArgument, currentValue in arguments:

                    if currentArgument in ("-h", "--Help"):
                        print("-playlist | -p  <playlistid>")

                    elif currentArgument in ("-p", "-playlist"):
                        result = option_playlist(currentValue.replace(" ", ""))
                        if result and len(result) == 2:
                            print("Successful:" + str(result[0]))
                            print("Errors:" + str(result[1]))


            else:
                print("Missing parameter")

        except getopt.error as err:
            print(str(err))

    else:
        print("No Parameter, running webserver")
        app.run()
