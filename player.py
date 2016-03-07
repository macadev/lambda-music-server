import os
import subprocess

class Player:

    @staticmethod
    def remove_song_from_queue(song_id, _shared_queue):
        for index, song in enumerate(_shared_queue):
            if song_id == song['id']:
                _shared_queue.pop(index)
                return


    @staticmethod
    def play_song(song):
        print('Playing song!')
        subprocess.call(['mpv', '--no-video', song['url']])


    @staticmethod
    def play_next_song():
        print('Killing mpv process!')
        p = subprocess.Popen(['pgrep', '-f', 'mpv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid, err = p.communicate()
        pid = pid.rstrip()
        subprocess.call(['kill', '-9', pid])


