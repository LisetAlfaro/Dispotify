"""This file has the principal node functions """

import Pyro4
import os
from Tools import *
from threading import Thread


@Pyro4.expose
class Client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.servers = []
        # self.servers.append('PYRO:server@127.0.0.1:8010')
        # self.servers.append('PYRO:server@127.0.0.1:8050')
        self.uri = get_uri_from_ip_and_port("client", ip, port)

        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'client')
        self.pyro = Thread(target=daemon.requestLoop)
        self.pyro.start()
    @property
    def get_ip(self):
        return self.ip

    @property
    def get_port(self):
        return self.port

    @property
    def get_uri(self):
        return self.uri

    def broadcast(self):
        for i in range(30):
            new_servers = do_broadcast(self.ip, self.port, self.uri)
            for l in new_servers:
                if "client" not in l and l not in self.servers:
                    self.servers.append(l)

    def loop(self):
        while True:
            self.broadcast()
            if len(self.servers) == 0 :
                print("Connecting...Wait a few seconds")
                continue
            dots = "\n\n" + '*' * 20 + "DSpotify" + '*' * 20 + "\n"
            print(dots)
            while True:

                action = input("\n Write the number of the action you want to do:\n 1-See list of music\n "
                               "2-Search a song\n 3-Play local music\n 4-Exit \n")
                if action not in ["1", "2", "3","4"]:
                    print("No valid option, please try again")
                    continue
                if action == "1":
                    for server in self.servers:
                        try:
                            s = Pyro4.Proxy(server)
                            music_list = s.get_all_music
                            for song in music_list:
                                print(song)
                            break  # I already know about all the servers
                        except Pyro4.errors.CommunicationError:
                            continue

                if action == "2":
                    print("What parameter will you use for the search")
                    print("1- Name")
                    print("2- Title")
                    print("3- Album")
                    print("4- Artist")

                    search_parameter = input("Write the number of the desire option\n")

                    song = ""
                    if search_parameter == "1":

                        song = input("What is the song's name?\n")

                        for server in self.servers:
                            titles_dic = {}
                            try:
                                s = Pyro4.Proxy(server)
                                music = s.get_all_music
                                go = False
                                while True:
                                    if go:
                                        break
                                    if song == "":
                                        break
                                    elif song not in music.keys():
                                        song = input("This song is not in the list, try again\n")
                                    else:
                                        for uri in music[song]:
                                            if not get_song_from_uri(song,uri):
                                                continue
                                            else:
                                                play_song(song, './')
                                                os.remove('./' + song)
                                                go = True
                                                break
                                        else:
                                            break
                                break
                            except Pyro4.errors.CommunicationError:
                                continue

                    elif search_parameter == "2":
                        for server in self.servers:
                            titles_dic = {}
                            try:
                                s = Pyro4.Proxy(server)
                                titles_dic = s.get_all_titles
                                print("This are the titles available:")

                                for titles in titles_dic.keys():
                                    print(titles)
                                    title = ""
                                while True:
                                    title = input("\nSelect the title you want or press enter to go back\n" )
                                    if title == "":
                                        break
                                    if title not in titles_dic:
                                        print("This title is not in the list, try again.")
                                    else:
                                        # title is in the list
                                        print("This songs has " + title + " as title:")
                                        for song in titles_dic[title]:
                                            print(song)

                                        while True:

                                            song = input("\nSelect a song to reproduce or press enter to set another "
                                                         "title\n")
                                            if song == "":
                                                break
                                            elif song not in titles_dic[title]:
                                                print("This song is not in the list, try again")
                                            else:
                                                # print("Song:" + song)
                                                # print(titles_dic[title][song])
                                                for uri in titles_dic[title][song]:
                                                    if not get_song_from_uri(song, uri) :
                                                        continue
                                                    else :
                                                        play_song(song, './')
                                                        os.remove('./' + song)

                                                        break
                                                else:
                                                    break
                                break
                            except Pyro4.errors.CommunicationError:
                                continue

                    elif search_parameter == "3":

                        for server in self.servers:
                            albums_dic = {}
                            try:
                                s = Pyro4.Proxy(server)
                                albums_dic = s.get_all_albums
                                print("This are the albums available:")
                            except Pyro4.errors.CommunicationError:
                                continue
                            for album in albums_dic.keys():
                                print(album)
                                album = ""
                            while True:
                                album = input("\nSelect the album you want or press enter to go back\n" )
                                if album == "":
                                    break
                                if album not in albums_dic:
                                    print("This album is not in the list, try again.")
                                else:
                                    # album is in the list
                                    print("This songs has " + album + " as album:")
                                    for song in albums_dic[album]:
                                        print(song)
                                    while True:
                                        song = input("\nSelect a song to reproduce or press enter to set another album\n")
                                        if song == "":
                                            break
                                        elif song not in albums_dic[album]:
                                            print("This song is not in the list, try again")
                                        else:

                                            for uri in albums_dic[album][song]:
                                                if not get_song_from_uri(song, uri):
                                                    continue
                                                else:
                                                    play_song(song, './')
                                                    os.remove('./' + song)
                                                    continue
                                            else:
                                                break

                    elif search_parameter == "4":

                        for server in self.servers:
                            albums_dic = {}
                            try:
                                s = Pyro4.Proxy(server)
                                artists_dic = s.get_all_artists
                                print("This are the albums available:")
                            except Pyro4.errors.CommunicationError:
                                continue
                            for artist in artists_dic.keys():
                                print(artist)
                                album = ""
                            while True:
                                artist = input("\nSelect the artist you want or press enter to go back\n" )
                                if artist == "":
                                    break
                                if artist not in artists_dic:
                                    print("This artist is not in the list, try again.")
                                else:
                                    # artist is in the list
                                    print("This songs has " + artist + " as artist:")
                                    for song in artists_dic[artist]:
                                        print(song)
                                    while True:
                                        song = input("\nSelect a song to reproduce or press enter to set another artist\n")
                                        if song == "":
                                            break
                                        elif song not in artists_dic[artist]:
                                            print("This song is not in the list, try again")
                                        else:

                                            for uri in artists_dic[artist][song] :
                                                if not get_song_from_uri(song, uri) :
                                                    continue
                                                else :
                                                    play_song(song, './')
                                                    os.remove('./' + song)
                                                    break
                                            else:
                                                break

                if action == "3":
                    path = input("Enter the folder of the music\n")
                    try:
                        folder_files = os.listdir(path)
                        print(folder_files)
                        music_list = []
                        for file in folder_files:
                            if file in music_list:
                                """It is already in the list"""
                                continue
                            extensions = ['.mp3', '.m4a', '.wav', '.wma']
                            if file[-4 :] in extensions and file not in music_list:
                                music_list.append(file)
                        print("\nThis is your music, select one of them to play or type exit() to do another thing"
                              "\n")
                        for music in music_list:
                            print("- " + music)
                        while True:
                            selected_song = input()
                            if selected_song == "":
                                break
                            if selected_song in music_list:
                                while True :
                                    play_song(selected_song, path)
                                    break
                            else:
                                print("You don't have that song in your list, please check if the name is correct")
                    except:
                        print("Can't open the folder or not found songs in it, please try again")

                if action == "4":
                    print("\n Come back soon")
                    break


if __name__ == '__main__':

    ip, port = input("Set ip and port separated by :\n").split(":")
    node = Client(ip, port)

    node.loop()

