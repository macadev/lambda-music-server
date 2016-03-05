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
        os.remove(song_info['filename'])

    def play_song(song):
        print('Playing song!', song['filename'])
        subprocess.call(['mpg123', song['filename']])

    def play_next_song(self):
        pass


