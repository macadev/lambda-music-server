from flask import Flask, request, render_template
import os
import time
import glob
import subprocess

from celery import Celery
class ref:
    def __init__(self, obj):
        with open('current_song.secret', 'w') as f:
            f.write(str(obj))
            f.close()
        #self.obj = obj

    def get(self):
        #return self.obj
        with open('current_song.secret', 'r') as f:
            c = f.readline()
            f.close()
            return int(c.rstrip())

    def set(self, obj):
        with open('current_song.secret', 'w') as f:
            f.write(str(obj))
            f.close()


application = Flask(__name__)

redis_url = os.environ.get('REDIS_URL')
if redis_url is None:
    redis_url = 'redis://localhost:6379/0'

# Redis and Celery configuration
application.config['BROKER_URL'] = redis_url
application.config['CELERY_RESULT_BACKEND'] = redis_url

celery = Celery(application.name, broker=redis_url)
celery.conf.update(BROKER_URL=redis_url,
                CELERY_RESULT_BACKEND=redis_url)

@application.route("/")
def hello():
    return render_template('index.html', page='index')

song_id = 0
#current_song_playing = 0
current_song_playing = ref(0)

@application.route("/submit", methods=['POST'])
def submit_song():
    global song_id
    # determine whether soundcloud or youtube

    if request.method == 'POST':
        print("Processing incoming song request")
        song_url = request.form['song_url']
        print(song_url)
        name = request.form['name']
        print(name)

        source_type = None
        if 'youtube.com' in song_url:
            source_type = 'youtube'
            print('source type is youtube!')
        elif 'soundcloud.com' in song_url:
            source_type = 'soundcloud'
            print('source type is soundcloud!')
        else:
            return "Invalid URL. Only Youtube and Soundcloud links allowed!"

        process_song_request.delay(song_url, name, source_type, song_id)
        song_id = song_id + 1
        return render_template('success.html', page='success')
    else:
        return "Malformed request."

@application.route("/next-song")
def next_song():
    p = subprocess.Popen(['pgrep', '-f', 'mpg123'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    pid, err = p.communicate()
    pid = pid.rstrip()
    subprocess.call(['kill', '-9', pid])
    return render_template('index.html', page='index')

@celery.task
def add(x,y):
    z = x+y
    print(z)

@celery.task
def process_song_request(song_url, name, source_type, song_id):
    global current_song_playing
    if source_type == 'youtube':
        #subprocess.call(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', song_url, '-o', 'song.mp3'])
        subprocess.call(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', song_url])
    else:
        subprocess.call(['scdl', '-l', song_url, '--onlymp3'])
        #subprocess.call(['mv', '*.mp3', 'song.mp3'])

    while song_id != current_song_playing.get():
        time.sleep(0.5)
        #print("cuurent song id: ", current_song_playing.get())
        #print("my song id: ", song_id)

    most_recent_file = max(glob.iglob('*.[Mm][Pp4][3Aa]'), key=os.path.getctime)

    if '.m4a' in most_recent_file:
        tmp_name = most_recent_file.split('.')[0]
        tmp_name = tmp_name + '.mp3'
        subprocess.call(['ffmpeg', '-i', most_recent_file, '-acodec', 'libmp3lame', '-ab', '128k', tmp_name])
        most_recent_file = tmp_name

    print("cuurent song id: ", current_song_playing.get())
    subprocess.call(['mpg123', most_recent_file])
    print("done playing ", most_recent_file)
    current_song_playing.set(current_song_playing.get() + 1)
    print("current song is now: ", current_song_playing.get())
    #os.remove('song.mp3')
    subprocess.call(['rm', most_recent_file])

@application.route("/success", methods=['POST'])
def submit_song_success():
    global song_id
    # determine whether soundcloud or youtube

    if request.method == 'POST':
        print("Processing incoming song request")
        song_url = request.form['song_url']
        print(song_url)
        name = request.form['name']
        print(name)

        source_type = None
        if 'youtube.com' in song_url:
            source_type = 'youtube'
            print('source type is youtube!')
        elif 'soundcloud.com' in song_url:
            source_type = 'soundcloud'
            print('source type is soundcloud!')
        else:
            return "Invalid URL. Only Youtube and Soundcloud links allowed!"

        process_song_request.delay(song_url, name, source_type, song_id)
        song_id = song_id + 1
        return render_template('success.html', page='success')
    else:
        return "Malformed request."


if __name__ == "__main__":
    application.run(host='0.0.0.0')
