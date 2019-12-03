"""This file has the principal node functions """

import Pyro4
import os
from Tools import *
from threading import Thread



@Pyro4.expose
class ClientNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.servers = []
        self.servers.append('PYRO:server@127.0.0.1:8000')
        self.uri = get_uri_from_ip_and_port("client", ip, port)

        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'client')
        Thread(target=daemon.requestLoop).start()

    @property
    def my_music_folder_path(self):
        return "./my_music/"

    def broadcast(self):
        for i in range(20):
            new_servers = do_broadcast(self.ip, self.port, self.uri)
            for l in new_servers:
                if l not in self.severs:
                    self.servers.append(l)

    def loop(self):
        while True:
            # self.broadcast()
            # if len(self.servers) == 0:
            #     print("Nobody answer, please wait")
            #     continue
            # else:
            #     print(self.servers)
            dots = '*' * 20 + "DSpotify" + '*' * 20
            print(dots)
            action = input("Write the number of the action you want to do:\n 1-See list of music\n "
                           "2-Search a song\n 3-Play music\n")
            if action not in ["1", "2", "3","exit()"]:
                print("No valid option, please try again")
                continue
            if action == "1":
                server = Pyro4.Proxy(self.servers[0])
                music_list = server.get_song_list
                # TODO pagination of songs later
                for song in music_list:
                    print(song)
                    continue

            if action == "2":
                print("Which parameter you'll use for the search")
                print("1- Name")
                print("2- Title")
                print("3- Album")
                print("4- Artist")

                search_parameter = input("Write the number and press Enter\n")

                if search_parameter == "1":
                    song = input("Write the name of the song and press Enter\n")
                    server = Pyro4.Proxy(self.servers[0])
                    result = get_song_for_search(1, song, server.get_uri)
                    if result == "Yes":
                        answer = input("Song founded...Do you wish download it?...\nSay Yes or No\n")
                        if answer == "Yes":
                            try:
                                print('pasando Uri')
                                get_song_from_uri(song,self.uri, server.get_uri)
                            except:
                                print("It was not possible download the song, please try again")
                                continue

                        elif answer == "No":
                            continue

                    else:
                        print("Song not found")

                if search_parameter == "2":
                    song_title = input("Write the title of the song and press \'enter\'")
                    server = Pyro4.Proxy(self.servers[0])
                    result = get_song_for_search(2, song_title, server.get_uri)

                    for song in result:
                        print(song)

                    answer = input("This songs are founded\n"
                                   "If you wish download one please write the name and press \'enter\' or write "
                                   "\"exit()\" to do another thing")
                    if answer == "exit()":
                        continue
                    else:
                        try:
                            get_song_from_uri(song, server.get_uri)
                        except:
                            print("It was not possible download the song, please try again")
                            continue

                if search_parameter == "3":

                    song_album = input("Write the album's name and press \'enter\'")
                    server = Pyro4.Proxy(self.servers[0])
                    result = get_song_for_search(3, song_album, server.get_uri)

                    for song in result:
                        print(song)

                    answer = input("This songs are founded\n"
                                   "If you wish download one please write the name and press \'enter\' or write "
                                   "\"exit()\" to do another thing")
                    if answer == "exit()":
                        continue
                    else:
                        try:
                            get_song_from_uri(song, server.get_uri)
                        except:
                            print("It was not possible download the song, please try again")
                            continue

                if search_parameter == "4":

                    song_artist = input("Write the album's name and press \'enter\'")
                    server = Pyro4.Proxy(self.servers[0])
                    result = get_song_for_search(4, song_artist, server.get_uri)

                    for song in result:
                        print(song)

                    answer = input("This songs are founded\n"
                                   "If you wish download one please write the name and press \'enter\' or write "
                                   "\"exit()\" to do another thing")
                    if answer == "exit()":
                        continue
                    else:
                        try:
                            get_song_from_uri(song, server.get_uri)
                        except:
                            print("It was not possible download the song, please try again")
                            continue

            if action == "3":
                my_music_list = get_my_music_list("./my_music/")
                print("\nThis is your music, select one of them to play\n")

                for music in my_music_list:
                    print("- " + music)
                while True:
                    selected_song = input()
                    if selected_song == "exit()":
                        break
                    if selected_song in my_music_list:
                        while True:
                            play_song(selected_song, "./my_music/")
                            break
                    else:
                        print("You don't have that song in your list, please check if you write correctly the name")

            if action == "exit()":
                print("\n Come back soon")
                break


if __name__ == '__main__':
    node = ClientNode("127.0.0.1", "8056")
    node.loop()
