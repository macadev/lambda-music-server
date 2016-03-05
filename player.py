import os
import subprocess

class Player:

    @staticmethod
    def remove_song_from_queue(song_id, _shared_queue):
        for index, song in enumerate(_shared_queue):
            if song_id == song['id']:
                Player.delete_song(_shared_queue[index])
                _shared_queue.pop(index)
                return


    @staticmethod
    def delete_song(song_info):
        try:
            os.remove(song_info['filename'])
        except FileNotFoundError:
            print('File does not exist')


    @staticmethod
    def play_song(song):
        print('Playing song!', song['filename'])
        subprocess.call(['mpg123', song['filename']])


    @staticmethod
    def play_next_song():
        print('Killing mpg123 process!')
        p = subprocess.Popen(['pgrep', '-f', 'mpg123'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid, err = p.communicate()
        pid = pid.rstrip()
        subprocess.call(['kill', '-9', pid])


