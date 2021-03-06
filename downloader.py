import youtube_dl
import time
import requests
import subprocess
import uuid

from scdl import soundcloud
from stdoutcapture import Capturing

arguments = None
token = ''
path = ''
offset = 0
scdl_client_id = '95a4c0ef214f2a4a0852142807b54b35'

url = {
    'favorites': ('https://api.soundcloud.com/users/{0}/favorites?'
                  'limit=200&offset={1}'),
    'tracks': ('https://api.soundcloud.com/users/{0}/tracks?'
               'limit=200&offset={1}'),
    'all': ('https://api-v2.soundcloud.com/profile/soundcloud:users:{0}?'
            'limit=200&offset={1}'),
    'playlists': ('https://api.soundcloud.com/users/{0}/playlists?'
                  'limit=200&offset={1}'),
    'resolve': ('https://api.soundcloud.com/resolve?url={0}'),
    'me': ('https://api.soundcloud.com/me?oauth_token={0}')
}

client = soundcloud.Client(client_id=scdl_client_id)

def my_hook(d):
        if d['status'] == 'finished':
            print('Completed download. Beginning conversion.')
        if d['filename'] is not None:
            print("$$$FILENAME$$$: " + d['filename'])

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec':'mp3',
    }],
    'progress_hooks': [my_hook],
    'forcefilename': True
}

class Downloader:

    # Refactor this bit of shitty code.
    @staticmethod
    def get_youtube_song_metadata(song_url):
        song_info = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(song_url, download=False)
        song_info = Downloader.__filter_metadata(song_info, 'youtube', song_url)
        return song_info

    @staticmethod
    def get_soundcloud_song_metadata(song_url):
        song_info = Downloader.__get_soundcloud_song_metadata(song_url)
        return song_info

    @staticmethod
    def __get_soundcloud_song_metadata(song_url):
        song_info = {}
        try:
            item_url = url['resolve'].format(song_url)
            item_url = '{0}&client_id={1}'.format(item_url, scdl_client_id)
            r = requests.get(item_url)
            item = r.json()
            song_info = Downloader.__filter_metadata(item, 'soundcloud', song_url)
        except Exception:
            time.sleep(5)
            try:
                r = requests.get(item_url)
                item = r.json()
                song_info = Downloader.__filter_metadata(item, 'soundcloud', song_url)
            except Exception as e:
                print("Failed to obtain soundcloud song metadata")
        return song_info

    @staticmethod
    def __filter_metadata(metadata, source, url):
        song_info_to_keep = {}
        song_info_to_keep['id'] = str(uuid.uuid4())
        song_info_to_keep['title'] = metadata['title']
        song_info_to_keep['url'] = url
        song_info_to_keep['source'] = source
        # TODO: Fix issues with duration
        if source is 'soundcloud':
            song_info_to_keep['duration'] = str(int((metadata['duration'] / 1000) / 60)) + ':' + str(int((metadata['duration']/1000)) % 60)
        else:
            song_info_to_keep['duration'] = str(int(metadata['duration'])) + str(metadata['duration'] % 60)
        return song_info_to_keep
