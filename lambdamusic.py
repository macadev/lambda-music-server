import os
import subprocess
import sys
import json

from flask import Flask, request, render_template, flash
from multiprocessing import Manager, Pool
from downloader import Downloader

application = Flask(__name__)

# Set the secret key to enable cookies
application.secret_key = 'some secret key'
application.config['SESSION_TYPE'] = 'filesystem'

process_pool = None
manager = Manager()
shared_queue = manager.list()
playing = manager.Value('i', 0)

@application.route("/")
def hello():
    return render_template('index.html', page='index')

@application.route("/submit", methods=['POST'])
def submit_song():
    global playing
    print("Processing incoming song request")
    song_url = request.form['song_url']
    print(song_url)
    name = request.form['name']
    print(name)

    if 'youtube.com' in song_url:
        source_type = 'youtube'
        print('source type is youtube!')
    elif 'soundcloud.com' in song_url:
        source_type = 'soundcloud'
        print('source type is soundcloud!')
    else:
        return "Invalid URL. Only Youtube and Soundcloud links allowed!"

    if playing.value is 0:
        print('playing is 0!!!')
        playing.value = 1
        # How do I apply a callback without passing retval down the chain?
        process_pool.apply_async(add_song_to_queue, [song_url, name, source_type], callback=run_through_queue)
    else:
        process_pool.apply_async(add_song_to_queue, [song_url, name, source_type])

    print(len(shared_queue))
    flash('Song added successfully!')
    return render_template('index.html')

@application.route("/playlist", methods=['GET', 'POST'])
def get_playlist():
    global playing
    playlist = []
    i = 0
    queue_size = len(shared_queue)
    while i < queue_size:
        print(shared_queue[i])
        playlist.append(shared_queue[i])
        i = i + 1
    return json.dumps(playlist)

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
    shared_queue.append(song_info)
    print(len(shared_queue))

def run_through_queue(_):
    try:
        while True:
            song = shared_queue[0]
            print('Playing song!', song.get('filename'))
            subprocess.call(['mpg123', song.get('filename')])
            # delete the song from queue
            print("Deleting song!")
            os.remove(song.get('filename'))
            del shared_queue[0]
    except:
        print("Unexpected error:", sys.exc_info())
        playing.value = 0
        pass

if __name__ == "__main__":
    process_pool = Pool()
    try:
        application.run(host='0.0.0.0', debug=True)
    except KeyboardInterrupt:
        process_pool.close()
        process_pool.join()
