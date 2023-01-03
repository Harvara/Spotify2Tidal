import getopt
import sys

from dotenv import load_dotenv
from Spotify import Spotify
from Tidal import Tidal

load_dotenv()


def move_playlist(playlist, name, tidal):
    new_playlist = tidal.session.user.create_playlist(name, "Moved by script")
    for playlist_item in playlist['tracks']['items']:
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
                print("Alternative: " + found_tracks[0].name +  " by " + found_tracks[0].artist.name)
        else:
            print("No match found for: " + query)


def option_playlist(playlist_id):
    spotify = Spotify()
    tidal = Tidal()
    tidal.connect()


    playlist = spotify.get_playlist(playlist_id)
    if playlist:
        playlist_name = playlist["name"]
        move_playlist(playlist, playlist_name, tidal)




if __name__ == '__main__':

    if len(sys.argv) > 0:
        argument_list = sys.argv[1:]
        options = 'hp:'
        long_options = ['help', 'user=','subreddit=']
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

