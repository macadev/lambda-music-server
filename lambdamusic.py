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

@application.route("/")
def hello():
    playlist = list(_shared_queue)
    return render_template('index.html', playlist=playlist)

@application.route("/submit", methods=['POST'])
def submit_song():
    global _playing

    song_url = request.form['song_url']
    print(song_url)
    name = request.form['name']

    if 'youtube.com' in song_url:
        source_type = 'youtube'
    elif 'soundcloud.com' in song_url:
        source_type = 'soundcloud'
    else:
        return "Invalid URL. Only Youtube and Soundcloud links allowed!"

    if _playing.value is 0:
        _playing.value = 1
        # How do I apply a callback without passing retval down the chain?
        _process_pool.apply_async(add_song_to_queue, [song_url, name, source_type], callback=run_through_queue)
    else:
        _process_pool.apply_async(add_song_to_queue, [song_url, name, source_type])

    flash('Song added successfully!')
    playlist = list(_shared_queue)
    return render_template('index.html', playlist=playlist)

@application.route("/remove-song", methods=['POST'])
def remove_song():
    if request.headers['Content-Type'] == 'application/json':
        request_json = request.get_json()
        song_id = request_json['song_id']
        Player.remove_song_from_queue(song_id, _shared_queue)


@application.route("/next-song")
def next_song():
    p = subprocess.Popen(['pgrep', '-f', 'mpg123'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    pid, err = p.communicate()
    pid = pid.rstrip()
    subprocess.call(['kill', '-9', pid])
    return render_template('index.html', page='index')

def add_song_to_queue(song_url, submitter_name, source_type):
    if source_type == 'youtube':
        song_info = Downloader.download_youtube_song(song_url, submitter_name)
    else:
        song_info = Downloader.download_soundcloud_song(song_url, submitter_name)
    _shared_queue.append(song_info)
    print(len(_shared_queue))

def run_through_queue(_):
    try:
        while True:
            song = _shared_queue[0]
            Player.play_song(song)
            # delete the song from queue
            Player.remove_song_from_queue(song['id'], _shared_queue)
    except:
        print("Unexpected error:", sys.exc_info())
        _playing.value = 0
        pass

if __name__ == "__main__":
    _process_pool = Pool()
    try:
        application.run(host='0.0.0.0', debug=True)
    except KeyboardInterrupt:
        _process_pool.close()
        _process_pool.join()