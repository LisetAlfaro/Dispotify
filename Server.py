"""this is a distributed server, here are the functions to connect with other servers and serve clients"""
from Tools import *
from threading import Thread
import time


@Pyro4.expose
class Server:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.uri = get_uri_from_ip_and_port("server", ip, port)

        self.my_music = {}
        self.shared_music = {}

        self.my_music_folder_path = "./my_music/"
        self.shared_music_path = "./shared_music/"

        self._artist_dic = {}  # for artist have the songs
        self._album_dic = {}  # for album have the songs
        self._title_dic = {}  # for title have the songs

        self._my_music_size = get_dir_size(self.my_music_folder_path)
        self._shared_music_size = get_dir_size(self.shared_music_path)

        self.my_music = self.get_my_music_list(self.my_music_folder_path)
        self.shared_music = self.get_my_music_list(self.shared_music_path)

        self.list_uri = []
        # self.list_uri.append("Pyro:server@127.0.0.1:8050")
        # self.list_uri.append("Pyro:server@127.0.0.1:8010")

        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'server')
        Thread(target=daemon.requestLoop).start()

        self.server_loop()

    @property
    def get_uri(self):
        return self.uri

    @property
    def get_music(self):
        return self.my_music

    @property
    def get_all_my_music(self):
        music = []
        for song in self.my_music:
            if song not in music:
                music.append(song)

        for song in self.shared_music:
            if song not in music:
                music.append(song)
        return music

    @property
    def get_shared_music(self):
        return self.shared_music

    @property
    def get_title_music(self):
        return self._title_dic

    @property
    def get_album_music(self):
        return self._album_dic

    @property
    def get_artist_music(self):
        return self._artist_dic

    @property
    def get_all_music(self):
        music_list = {}
        for server_uri in self.list_uri:
            try:
                # print("Conectandome a " + server_uri)
                s = Pyro4.Proxy(server_uri)
                # print("Server music: ")
                # print(s.get_music)
                for song in s.get_music:
                    # print("Song:" + song)
                    if song not in music_list:
                        music_list[song] = [server_uri]
                    else:
                        music_list[song].append(server_uri)
                for song in s.get_shared_music:
                    if song not in music_list:
                        music_list[song] = [server_uri]
                    else:
                        music_list[song].append(server_uri)
            except Pyro4.errors.CommunicationError:
                continue

        return music_list

    @property
    def get_all_titles(self):
        titles = {}
        for uri in self. list_uri:
            try:
                server = Pyro4.Proxy(uri)
                # for each title in server's_music
                server_titles = server.get_title_music
                for title in server_titles.keys():
                    # if I already haven't this title, creat it
                    if title not in titles:
                        titles[title] = {}
                        # for each song
                    for song in server_titles[title]:
                        # If I already haven't it
                        if song not in titles[title]:
                            titles[title][song] = [uri]
                        else:
                            titles[title][song].append(uri)
            except Pyro4.errors.CommunicationError:
                continue
        else:
            return titles

    @property
    def get_all_albums(self):
        albums = {}
        for uri in self.list_uri :
            try :
                server = Pyro4.Proxy(uri)
                # for each title in server's_music
                server_albums = server.get_album_music
                for album in server_albums.keys():
                    # if I already haven't this title, creat it
                    if album not in albums:
                        albums[album] = {}
                        # for each song
                    for song in server_albums[album]:
                        # If I already haven't it
                        if song not in albums[album]:
                            albums[album][song] = [uri]
                        else:
                            albums[album][song].append(uri)

            except Pyro4.errors.CommunicationError:
                continue
        else :
            return albums

    @property
    def get_all_artists(self):
        artists = {}
        for uri in self.list_uri :
            try :
                server = Pyro4.Proxy(uri)
                # for each title in server's_music
                server_artists = server.get_artist_music
                for artist in server_artists.keys() :
                    # if I already haven't this title, creat it
                    if artist not in artists :
                        artists[artist] = {}
                        # for each song
                    for song in server_artists[artist] :
                        # If I already haven't it
                        if song not in artists[artist] :
                            artists[artist][song] = [uri]
                        else:
                            artists[artist][song].append(uri)
            except Pyro4.errors.CommunicationError :
                continue
        else :
            return artists

    def replicate(self):
        count_of_music = []
        uris = self.list_uri
        for song in self.get_all_my_music:
            count = 0
            for uri in uris:
                try:
                    s = Pyro4.Proxy(uri)
                    if song in s.get_all_my_music:
                     count += 1

                except Pyro4.errors.CommunicationError:
                    continue
            count_of_music.append([count,song])

        for counter in count_of_music:
            count = counter[0]
            song = counter[1]
            if count == 4:
                break
            else:
                for uri in uris:
                    if uri == self.uri:
                        continue
                    try:
                        s = Pyro4.Proxy(uri)
                        if song not in s.get_all_my_music:
                            self.push_song_to_uri(song,s.get_uri)
                            count -= 1
                    except Pyro4.errors.CommunicationError:
                        continue

    def get_my_music_list(self, path):
        folder_files = os.listdir(path)
        music_list = {}
        for file in folder_files:
            if file in music_list :
                """It is already in the list"""
                continue
            extensions = ['.mp3', '.m4a', '.wav', '.wma']
            if file[-4 :] in extensions :
                """It's a valid audio file"""
                file_title = "Unknown"
                file_album = "Unknown"
                file_artist = "Unknown"
                try:
                    audio_file: EasyID3 = EasyID3(path + file)
                    if audio_file is None:
                        continue
                    file_title = audio_file["title"][0]
                    file_album = audio_file["album"][0]
                    file_artist = audio_file["artist"][0]
                    music_list[file] = (file_title, file_album, file_artist)
                except:
                    music_list[file] = (file_title, file_album, file_artist)


                if file_title not in self._title_dic :
                    self._title_dic[file_title] = [file]
                elif file not in self._title_dic[file_title] :
                    self._title_dic[file_title].append(file)

                if file_album not in self._album_dic :
                    self._album_dic[file_album] = [file]
                elif file not in self._album_dic[file_album] :
                    self._album_dic[file_album].append(file)

                if file_artist not in self._artist_dic :
                    self._artist_dic[file_artist] = [file]
                elif file not in self._artist_dic[file_artist] :
                    self._artist_dic[file_artist].append(file)

        return music_list

    def update_my_music(self):
        while True:
            my_music_actual_size = get_dir_size(self.my_music_folder_path)

            shared_music_actual_size = get_dir_size(self.shared_music_path)

            if my_music_actual_size != self._my_music_size:
                self.my_music = self.get_my_music_list(self.my_music_folder_path)
                self._my_music_size = my_music_actual_size

            if shared_music_actual_size != self._shared_music_size:
                self.shared_music = self.get_my_music_list(self.shared_music_path)
                self._shared_music_size = shared_music_actual_size
            time.sleep(40)

    def wait_for_get(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 1000))
        sock.listen(100)
        # print('Waiting for request connection')

        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()
            # If is a GET requirement
            if data[:3] == 'GET':
                required_song = data[4:]

                # If I have the song

                if required_song in self.my_music or required_song in self.shared_music:
                    try:
                        s.send(b"OK")
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                            ConnectionRefusedError, OSError):
                        s.close()
                        continue
                    # Finishing handshake
                    expected_ACK = s.recv(2).decode()
                    if expected_ACK == "OK":
                        # Sending selected song
                        try:
                            file = open(self.my_music_folder_path + required_song, "rb")
                        except FileNotFoundError:
                            file = open(self.shared_music_path + required_song, "rb")
                        while True:
                            chunk = file.read(1024)
                            if not chunk:
                                break
                            try:
                                s.sendall(chunk)
                            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                    ConnectionRefusedError):
                                break
                        file.close()
                else:
                    try:
                        s.send(b"Error 404 Song not found")
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                            ConnectionRefusedError):
                        pass
                    break
            else:
                print("Fail in GET protocol")
            s.close()
        sock.close()

    def push_song_to_uri(self, song, uri):
        """
        Send the selected song to the selected uri
        Params:
        song: selected song
        uri: selected uri
        """

        # Get node from uri
        try:
            node = Pyro4.Proxy(uri)
        except (Pyro4.errors.CommunicationError, Pyro4.errors.PyroError) :
            return

        # Get ip and port from the current uri
        ip, port = get_ip_and_port_from_uri(uri)

        # I stablish a TCP connection
        try :
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port) + 3000))
        except (ConnectionRefusedError, OSError) :
            return

        # Send PUSH request
        data = 'PUSH' + ' ' + song
        try :
            s.send(data.encode())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
                OSError) :
            return
        raw_recv_data = s.recv(3)
        recv_data = raw_recv_data.decode()

        if recv_data == 'ACK' :
            # Finsish handshake
            data = 'ACK'
            try :
                s.send(data.encode())
            except (
            BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
            OSError) :
                return

            # Sending selected song
            try :
                file = open(self.my_music_folder_path + song, "rb")
            except FileNotFoundError :
                file = open(self.shared_music_path + song, "rb")

            while (True) :
                chunk = file.read(65536)
                if not chunk :
                    break
                try :
                    s.sendall(chunk)
                except (
                BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
                OSError) :
                    break

            file.close()
        else :
            print("Fail in PUSH protocol")
        s.close()

    def wait_for_push(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 3000))
        sock.listen(100)

        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()

            # If is a GET requirement
            if data[:4] == 'PUSH' :
                required_song = data[5 :]

                try:
                    s.send(b"ACK")
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                        ConnectionRefusedError, OSError):
                    s.close()
                    continue

                expected_ACK = s.recv(3).decode()

                if (expected_ACK == "ACK"):
                    # Open the file descriptor for receive the song
                    # and write into it
                    f = open(self.shared_music_path + required_song, "wb")

                    while True:
                        try:
                            input_data = s.recv(1024)
                            if not input_data:
                                break
                            else:
                                f.write(input_data)
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            print("Error receiving the file")
                            os.remove(Server.shared_music + required_song)
                            break

                    f.close()
                else:
                    print("Fail in the PUSH protocol")
            s.close()
        sock.close()

    def waiting_to_broadcast(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(('', self.port + 4000))

        while True :
            data, addr = client.recvfrom(len("VALARMORGHULIS"))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while True :
                try :
                    sock.connect((addr[0], addr[1]))
                    break
                except (ConnectionRefusedError, OSError) :
                    # print("Can't connect to " + str((addr[0], addr[1])))
                    continue
            try :
                sock.send(str(self.uri).encode())
            except (
                    BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                    ConnectionRefusedError) :
                continue

        client.close()

    def server_replication_loop(self):
        while True:
            self.replicate()
            time.sleep(35)

    def server_loop(self):

        # Listening for broadcast
        Thread(target=self.waiting_to_broadcast).start()

        # Waiting for get and push requests

        Thread(target=self.wait_for_get).start()
        Thread(target=self.wait_for_push).start()

        # Update my properties
        Thread(target=self.update_my_music).start()

        # Replicate
        Thread(target=self.server_replication_loop).start()

        while True :
            for it in range(60) :
                servers_list = do_broadcast(self.ip, self.port, self.uri)
                for new_server in servers_list :
                    if new_server not in self.list_uri :
                        self.list_uri.append(new_server)
            time.sleep(40)


if __name__ == '__main__':
    ip, port = input("Set ip and port separated by :\n").split(":")
    server = Server(ip, port)


