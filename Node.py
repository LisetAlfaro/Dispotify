"""This file has the principal node functions """
"""Import zone"""
import socket
import os
# import vlc
# from mutagen.easyid3 import EasyID3


class Node:

    def __init__(self):
        self._my_music = {}

    def get_my_music_list(self):
        folder_files = os.listdir("./my_music")
        print("Files")
        print(folder_files)
        for file in folder_files:
            if file in self._my_music:
                """It is already in the list"""
                continue
            extensions = ['.mp3', '.m4a', '.wav', '.wma']
            print(extensions)
            print(file[-4:])
            if file[-4:] in extensions:
                print(file)
                """It's a valid audio file"""
                file_title = ""
                file_album = ""
                file_artist = ""
                try:
                    audio_file = None
                    # audio_file = EasyID3("./my_music"+file)
                    if audio_file is None:
                        continue
                    file_title = audio_file["title"][0]
                    file_album = audio_file["album"][0]
                    file_artist = audio_file["artist"][0]
                    self.my_music[file] = (file_title, file_album, file_artist)
                except:
                    self._my_music[file] = (file_title, file_album, file_artist)
                    continue

    def play_music(self):
        """reproduce music """
        pass


if __name__ == '__main__':
    node = Node()
    node.get_my_music_list()
