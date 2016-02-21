from flask import Flask, request, render_template
import os
import subprocess

from celery import Celery

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

@application.route("/submit", methods=['POST'])
def submit_song():

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

        process_song_request.delay(song_url, name, source_type)
        return "Your song was queued successfully!"
    else:
        return "Malformed request."


@celery.task
def add(x,y):
    z = x+y
    print(z)

@celery.task
def process_song_request(song_url, name, source_type):
    if source_type == 'youtube':
        subprocess.call(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', song_url, '-o', 'song.mp3'])
    else:
        subprocess.call(['scdl', '-l', song_url])
        subprocess.call(['mv', '*.mp3', 'song.mp3'])

    subprocess.call(['mpg123', 'song.mp3'])
    #os.remove('song.mp3')

if __name__ == "__main__":
    application.run(host='0.0.0.0')
