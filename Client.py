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
        self.servers.append('PYRO:server@127.0.0.1:8000')
        self.uri = get_uri_from_ip_and_port("client", ip, port)

        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'client')
        Thread(target=daemon.requestLoop).start()

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
            dots = "\n\n\n" + '*' * 20 + "DSpotify" + '*' * 20
            print(dots)
            action = input("Write the number of the action you want to do:\n 1-See list of music\n "
                           "2-Search a song\n 3-Play local music\n 4-Exit \n")
            if action not in ["1", "2", "3","4"]:
                print("No valid option, please try again")
                continue
            if action == "1":
                for server in self.servers:
                    try:
                        s = Pyro4.Proxy(server)
                        music_list = s.get_all_music
                        # TODO pagination of songs later
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

                if search_parameter == "1":
                    song = input("What is the song's name?\n")
                    for server in self.servers:
                        try:
                            s = Pyro4.Proxy(server)
                            result = get_song_for_search(1, song, s.get_uri)
                            if result == "Yes":
                                answer = input("Song founded...You want listen it?...[Y|n]\n")
                                if answer == "Y":
                                    try:
                                        get_song_from_uri(song, s.get_uri)
                                        play_song(song, './')
                                        os.remove('./' + song)

                                    except:
                                        print("It was not possible reproduce the song...")
                                        continue
                                # You don't want to do nothing with the song
                                elif answer == "n":
                                    break
                            elif result == "ALD":
                                print("Song not found")
                        except Pyro4.errors.CommunicationError:
                            continue
                    else:
                        continue

                if search_parameter == "2":
                    go_out = False
                    song_title = input("What's the song's title?\n")
                    for server in self.servers:
                        try:
                            s = Pyro4.Proxy(server)
                            result = get_song_for_search(2, song_title, s.get_uri)

                            for song in result:
                                print(song)

                            answer = input("This songs are founded("+str(result.__len__())+")\n"
                                           "If you want reproduce one please write the name or write \"exit()\" to do "
                                           "another thing")
                            if answer == "exit()":
                                go_out = True
                                break
                            else:
                                try:
                                    get_song_from_uri(answer, s.get_uri)
                                    play_song(answer, './')
                                    os.remove('./' + answer)
                                    go_out = True
                                    break
                                except:
                                    print("It was not possible reproduce the song ...\nPlease try search it again")
                                    go_out = True
                                    break
                        except Pyro4.errors.CommunicationError:
                            continue
                    else:
                        continue
                    # If client cancel the action or it was not possible reproduce the song
                    if go_out:
                        continue

                if search_parameter == "3":
                    song_album = input("What's the song's album's name?\n")
                    go_out = False
                    for server in self.servers:
                        try:
                            s = Pyro4.Proxy(server)
                            result = get_song_for_search(3, song_album, s.get_uri)

                            for song in result:
                                print(song)

                            answer = input("This songs are founded("+str(result.__len__())+")\n"
                                           "If you want reproduce one please write the name or write \"exit()\" to do "
                                           "another thing")
                            if answer == "exit()":
                                go_out = True
                                break
                            else:
                                try:
                                    get_song_from_uri(answer,s.get_uri)
                                    play_song(answer, './')
                                    os.remove('./' + answer)
                                    go_out = True
                                    break
                                except:
                                    print("It was not possible reproduce the song ...\nPlease try search it again")
                                    go_out = True
                                    break
                        except Pyro4.errors.CommunicationError:
                            continue
                    else:
                        continue
                    if go_out:
                        continue

                if search_parameter == "4":
                    song_artist = input("What's the artist' name?")
                    go_out = False
                    for server in self.servers:
                        try:
                            s = Pyro4.Proxy(server)
                            result = get_song_for_search(4, song_artist, s.get_uri)

                            for song in result:
                                print(song)

                            answer = input("This songs are founded\n If you want reproduce one please write the name "
                                           "or write \"exit()\" to do another thing")
                            if answer == "exit()":
                                go_out = True
                                break
                            else:
                                try:
                                    get_song_from_uri(answer, s.get_uri)
                                    play_song(answer, "./")
                                    os.remove("./" + answer)
                                    go_out = True
                                    break
                                except:
                                    print("It was not possible reproduce the song ...\nPlease try search it again")
                                    go_out = True
                                    break
                        except Pyro4.errors.CommunicationError:
                            continue
                    else:
                        continue

                    if go_out:
                        continue

            if action == "3":
                path = input("Enter the folder of the music")
                try:
                    folder_files = os.listdir(path)
                    music_list = []
                    for file in folder_files:
                        if file in music_list:
                            """It is already in the list"""
                            continue
                        extensions = ['.mp3', '.m4a', '.wav', '.wma']
                        if file[-4 :] in extensions and file not in music_list :
                            music_list.append(file)
                            print("\nThis is your music, select one of them to play or type exit() to do another thing"
                                  "\n")
                            for music in music_list:
                                print("- " + music)
                            while True:
                                selected_song = input()
                                if selected_song == "exit()":
                                    break
                                if selected_song in music_list:
                                    while True :
                                        play_song(selected_song, "./my_music/")
                                        break
                                else:
                                    print("You don't have that song in your list, please check if the name is correct")
                except:
                    print("Can't open the folder or not found songs in it, please try again")

            if action == "4":
                print("\n Come back soon")
                break


if __name__ == '__main__':
    node = Client("127.0.0.1", "8056")
    node.loop()
