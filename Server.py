"""this is a distributed server, here are the functions to connect with other servers and serve clients"""
from Tools import *
from threading import Thread

"""Here is the Chord implementation"""
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
        # print("music:")
        # print(self.my_music)
        # print("Shared:")
        # print(self.shared_music)
        self.list_uri = []
        # fill this list by broadcast

        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'server')
        Thread(target=daemon.requestLoop).start()

    @property
    def get_uri(self):
        return self.uri

    @property
    def get_music(self):
        return self.my_music

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
    def get_shared_music_list(self):
        return self.shared_music

    @property
    def get_all_music(self):
        music_list = []
        for server_uri in self.list_uri:
            try:
                # print("Conectandome a " + server_uri)
                s = Pyro4.Proxy(server_uri)
                # print("Server music: ")
                # print(s.get_music)
                for song in s.get_music:
                    # print("Song:" + song)
                    if song not in music_list:
                        music_list.append(song)
                for song in s.get_shared_music:
                    if song not in music_list:
                        music_list.append(song)
            except Pyro4.errors.CommunicationError:
                print("Can't connect with " + server_uri)
                continue

        return music_list

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
                file_title = ""
                file_album = ""
                file_artist = ""
                try:
                    audio_file: EasyID3 = EasyID3("./my_music/" + file)
                    if audio_file is None:
                        continue
                    file_title = audio_file["title"][0]
                    file_album = audio_file["album"][0]
                    file_artist = audio_file["artist"][0]
                    music_list[file] = (file_title, file_album, file_artist)
                    if file_title not in self._title_dic:
                        self._title_dic[file_title] = [file]
                    elif file not in self._title_dic[file_title]:
                        self._title_dic[file_title].append(file)

                    if file_album not in self._album_dic :
                        self._album_dic[file_album] = [file]
                    elif file not in self._album_dic[file_album]:
                        self._album_dic[file_album].append(file)

                    if file_artist not in self._artist_dic:
                        self._artist_dic[file_artist] = [file]
                    elif file not in self._artist_dic[file_artist]:
                        self._artist_dic[file_artist].append(file)

                except:
                    music_list[file] = (file_title, file_album, file_artist)
                    continue
        return music_list

    def update_my_music(self):
        my_music_actual_size = get_dir_size(self.my_music_folder_path)
        shared_music_actual_size = get_dir_size(self.shared_music_path)
        if my_music_actual_size != self._my_music_size:
            self.my_music = self.get_my_music_list(self.my_music_folder_path)
            self._my_music_size = my_music_actual_size
        if shared_music_actual_size != self._shared_music_size:
            self.shared_music = self.get_my_music_list(self.shared_music_path)
            self._shared_music_size = shared_music_actual_size

    # Client and servers ask for a song

    def wait_for_search(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 2000))
        sock.listen(100)

        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()

            # If is a SEARCH requirement
            if data[:6] == 'SEARCH':

                attribute = int(data[7])
                attribute_name = data[9:]

                # The search is by name
                if attribute == 1:
                    print("The search is by name")
                    if attribute_name in self.my_music or attribute_name in self.shared_music:
                        print(" I have the song")
                        # music_and_server_list[attribute_name].append(self.uri)
                        try:
                            data = 'Yes'
                            s.send(data.encode())
                            s.close()

                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            s.close()
                            continue
                    else:
                        try:
                            print("Asking to others for song")
                            # Ask to other servers for the song
                            for uri in self.list_uri:
                                try:
                                    serv = Pyro4.Proxy(uri)
                                    if attribute_name in serv.get_music or attribute_name in serv.get_shared_music:
                                        data = "Yes"
                                        s.send(data.encode())
                                        s.close()
                                        break
                                except Pyro4.errors.CommunicationError:
                                    continue
                            # If anybody have the song
                            else:
                                s.send("ALD".encode())
                                s.close()

                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            s.close()
                            continue
                # The search is by Title
                elif attribute == 2:
                    music_list = []
                    if self.uri not in self.list_uri:
                        self.list_uri.append(self.uri)
                    for uri in server.list_uri:
                        try:
                            server = Pyro4.Proxy(uri)
                            if attribute_name in server.get_title_music:
                                for song in server.get_title_music[attribute_name].Keys():
                                    if song not in music_list:
                                        music_list.append(song)
                        except Pyro4.errors.CommunicationError:
                            continue
                    for song in music_list:
                        try:
                            s.send(song.encode())
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                                s.close()
                                continue
                    else :
                        try:
                            s.send(b"ALD")
                            s.close()
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            s.close()
                            continue
                # The search is by album
                elif attribute == 3:
                    music_list = []
                    if self.uri not in self.list_uri:
                        self.list_uri.append(self.uri)
                    for uri in server.list_uri:
                        try:
                            server = Pyro4.Proxy(uri)
                            if attribute_name in server.get_album_music:
                                for song in server.get_album_music[attribute_name].Keys():
                                    if song not in music_list:
                                        music_list.append(song)
                        except Pyro4.errors.CommunicationError:
                            continue

                    for song in music_list:
                        try:
                            s.send(song.encode())
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError) :
                            s.close()
                            continue
                    else:
                        try:
                            s.send(b"ALD")
                            s.close()
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            s.close()
                            continue
                # The search is by artist
                elif attribute == 4:
                    music_list = []
                    if self.uri not in self.list_uri:
                        self.list_uri.append(self.uri)
                    for uri in server.list_uri :
                        try:
                            server = Pyro4.Proxy(uri)
                            if attribute_name in server.get_artist_music:
                                for song in server.get_artist_music[attribute_name]:
                                    if song not in music_list:
                                        music_list.append(song)
                        except Pyro4.errors.CommunicationError:
                            continue

                    for song in music_list:
                        try :
                            s.send(song.encode())
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError) :
                            s.close()
                            continue
                    else:
                        try:
                            s.send(b"ALD")
                            s.close()
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError) :
                            s.close()
                            continue
            else:
                print("Fail in the SEARCH protocol")
                s.close()
        sock.close()

    # Client and server take a song
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
                    expected_ACK = s.recv(1024).decode()
                    if expected_ACK == "OK":
                        # Sending selected song
                        try:
                            file = open(self.my_music_folder_path + required_song, "rb")
                        except FileNotFoundError:
                            file = open(self.shared_music_path + required_song, "rb")
                        while True:
                            chunk = file.read(65536)
                            if not chunk:
                                break
                            try:
                                s.sendall(chunk)
                            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                    ConnectionRefusedError):
                                break
                        file.close()

                # I haven't the song, I have to asks others for it
                else:
                    for uri in self.list_uri:
                        try:
                            s = Pyro4.Proxy(uri)
                        except:
                            continue

                        if required_song in s.get_music.Keys() or required_song in s.get_shared_music:
                            if get_song_from_uri(required_song, uri):
                                try:
                                    s.send(b"OK")
                                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                        ConnectionRefusedError, OSError):
                                    s.close()
                                    continue
                                # Finishing handshake
                                expected_ACK = s.recv(1024).decode()
                                if expected_ACK == "OK":
                                    # Sending selected song
                                    try :
                                        file = open("./" + required_song, "rb")
                                    except FileNotFoundError:
                                        continue
                                    while True:
                                        chunk = file.read(65536)
                                        if not chunk:
                                            break
                                        try:
                                            s.sendall(chunk)
                                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
                                                ConnectionError, ConnectionRefusedError):
                                            break
                                    file.close()

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

    # Servers replicate songs in shared music
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
                    f = open(Server.shared_music_path + required_song, "wb")

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

    def server_loop(self):
        while True:
            for it in range(20):
                servers_list = do_broadcast(self.ip, self.port, self.uri)
                for new_server in servers_list:
                    if new_server not in self.list_uri:
                        self.list_uri.append(new_server)

            # how many servers have my music?
            for uri in self.list_uri:
                try:
                    node = Pyro4.Proxy(uri)
                except (Pyro4.errors.CommunicationError, Pyro4.errors.PyroError) :
                    return


if __name__ == '__main__':

    server = Server("127.0.0.1", input("port"))
    server.list_uri.append("Pyro:server@127.0.0.1:" + input("Puerto del otro server"))
    server.list_uri.append(server.get_uri)
    Thread(target=server.wait_for_search).start()
    Thread(target=server.wait_for_get).start()

