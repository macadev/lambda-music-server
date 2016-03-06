import subprocess
import sys
import json

from flask import Flask, request, render_template, flash
from multiprocessing import Manager, Pool
from downloader import Downloader
from player import Player

application = Flask(__name__)

# Set the secret key to enable cookies
application.secret_key = 'some secret key'
application.config['SESSION_TYPE'] = 'filesystem'

_process_pool = None
_manager = Manager()
_shared_queue = _manager.list()
_playing = _manager.Value('i', 0)
_song_playing = _manager.dict()


@application.route("/")
def hello():
    return render_template('player.html')


@application.route("/submit", methods=['POST'])
def submit_song():
    global _playing

    if request.headers['Content-Type'] == 'application/json':
        request_json = request.get_json()
        song_url = request_json['song_url']
        print(song_url)

        if 'youtube.com' in song_url:
            source_type = 'youtube'
        elif 'soundcloud.com' in song_url:
            source_type = 'soundcloud'
        else:
            return json.dumps({'submission_status': 'failed'})

        if _playing.value is 0:
            _playing.value = 1
            # How do I apply a callback without passing retval down the chain?
            _process_pool.apply_async(add_song_to_queue, [song_url, source_type], callback=run_through_queue)
        else:
            _process_pool.apply_async(add_song_to_queue, [song_url, source_type])

        return json.dumps({'submission_status': 'succeeded'})
    return json.dumps({'submission_status': 'failed'})


@application.route("/remove-song", methods=['POST'])
def remove_song():
    if request.headers['Content-Type'] == 'application/json':
        request_json = request.get_json()
        song_id = request_json['song_id']

        Player.remove_song_from_queue(song_id, _shared_queue)
        try:
            if song_id == _song_playing.get('id'):
                Player.play_next_song()
        except:
            print('No need to cancel playback')

        return json.dumps({'remove_status':'succeeded'})
    else:
        return json.dumps({'remove_status':'failed'})


@application.route("/refresh-playlist", methods=['POST'])
def get_playlist():
    if request.headers['Content-Type'] == 'application/json':
        client_playlist_song_IDs = request.get_json()
        new_songs = {'songs' : []}
        for song in _shared_queue:
            if client_playlist_song_IDs.get(song['id']) is not 1:
                new_songs['songs'].append(song)
        return json.dumps(new_songs)
    else:
        return json.dumps({'refresh_status':'failed'})

def add_song_to_queue(song_url, source_type):
    if source_type == 'youtube':
        song_info = Downloader.download_youtube_song(song_url)
    else:
        song_info = Downloader.download_soundcloud_song(song_url)

    _shared_queue.append(song_info)
    print(len(_shared_queue))


def run_through_queue(_):
    global _song_playing
    try:
        while True:
            song = _shared_queue[0]
            _song_playing = song
            Player.play_song(song)
            # delete the song from queue
            Player.remove_song_from_queue(song['id'], _shared_queue)
    except:
        print("Unexpected error:", sys.exc_info())
        _song_playing = None
        _playing.value = 0
        pass


if __name__ == "__main__":
    _process_pool = Pool()
    try:
        application.run(host='0.0.0.0', debug=True)
    except KeyboardInterrupt:
        _process_pool.close()
        _process_pool.join()
