"""this is a distributed server, here are the functions to connect with other servers and serve clients"""
from Tools import *
from threading import Thread

"""Here is the Chord implementation"""
@Pyro4.expose
class Server:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.my_music = {}
        self.uri = get_uri_from_ip_and_port("server", ip, port)
        self.my_music_folder_path = "./my_music/musiquita/"
        self.shared_music_path = "./shared_music/"

        self.my_music = get_my_music_list(self.my_music_folder_path)
        print(self.my_music)
        # Initialize Daemon
        daemon = Pyro4.Daemon(self.ip, self.port)
        daemon.register(self, 'server')
        Thread(target=daemon.requestLoop).start()

    @property
    def get_uri(self):
        return self.uri

    @property
    def get_song_list(self):
        return self.my_music
        # right now only return the local music, later it'll return the entire list of music of all the different nodes

    def wait_for_search(self) -> object:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 2000))
        sock.listen(100)

        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()
            print("data: " + data)
            # If is a SEARCH requirement
            if data[:6] == 'SEARCH':

                attribute = int(data[7])
                attribute_name = data[9:]
                # The search is by name
                if attribute == 1:
                    if attribute_name in self.my_music:
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
                            s.send("ALD".encode())
                            s.close()

                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError):
                            s.close()
                            continue
                # The search is by Title
                elif attribute == 2:
                    # music_and_server_list[attribute_name] = []
                    for song in self.my_music:
                        if attribute_name == song[0]:
                            # music_and_server_list[attribute_name].append(self.uri)
                            try:
                                s.send(b"Yes")
                            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                    ConnectionRefusedError, OSError):
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
                # The search is by album
                elif attribute == 3:
                    for song in self.my_music:
                        if attribute_name == song[1]:
                            try:
                                s.send(b"Yes")
                                s.close()

                            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                    ConnectionRefusedError, OSError):
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
                    for song in self.my_music:
                        if attribute_name == song[2]:
                            try:
                                s.send(b"Yes")

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
                # If I have the song I send the song
                if required_song in self.my_music:
                    try:
                        s.send(b"ValarMorghulis")
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                            ConnectionRefusedError, OSError):
                        s.close()
                        continue
                    # Finishing handshake
                    expected_ACK = s.recv(1024).decode()
                    if expected_ACK.find("ValarDohaeris") > -1:
                        client_uri = expected_ACK[expected_ACK.find(":") + 1 :]
                        client = Pyro4.Proxy(client_uri)
                        # Sending selected song
                        try:
                            file = open(self.my_music_folder_path + required_song, "rb")
                        except FileNotFoundError:
                            print("file not found error")

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

                # Else print the error 404
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

    def wait_for_push(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 3000))
        sock.listen(100)

        # print('Waiting for request connection')

        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()

            # If is a GET requirement
            if data[:4] == 'PUSH' :
                required_song = data[5 :]

                # If I can receive the song I send ACK
                try :
                    s.send(b"ACK")
                except (
                BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
                OSError) :
                    s.close()
                    continue

                # Finishing handshake
                expected_ACK = s.recv(3).decode()

                if (expected_ACK == "ACK") :
                    # Open the file descriptor for receive the song
                    # and write into it
                    f = open(Server.shared_music_path + required_song, "wb")

                    while True :
                        try :
                            # Recibir datos del cliente.
                            # print('Recibiendo paquete')
                            input_data = s.recv(1024)
                            if not input_data :
                                break
                            else :
                                f.write(input_data)
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                                ConnectionRefusedError, OSError) :
                            print("Hubo un error recibiendo el archivo")
                            os.remove(Server.shared_music + required_song)
                            break

                    f.close()
                else :
                    print("Fallo en el protocolo PUSH")
            s.close()
        sock.close()

    def waiting_for_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.ip, self.port + 1000))
        sock.listen(100)
        while True:
            s, addr_info = sock.accept()

            data = s.recv(1024).decode()

            # If is a GET requirement
            if data[:3] == 'GET':
                required_song = data[4:]

                # If I have the song I send the song
                if required_song in self.my_music:
                    s.send(b"ValarMorghulis")
                    # Finishing handshake
                    rec_ack = s.recv(13).decode()
                    if rec_ack == "ValarDohaeris":
                        # Sending selected song
                        file = open(Server.my_music_folder_path + required_song, "rb")
                        while True:
                            chunk = file.read(65536)
                            if not chunk:
                                break
                            s.sendall(chunk)
                        file.close()

                # Else print the error 404
                else:
                    s.send(b"Error 404 Song not found")
                    break

            if data[:4] == 'PUSH':
                required_song = data[5:]

                # If I can receive the song I send ACK
                s.send(b"ACK")

                # Finishing handshake
                expected_ack = s.recv(3).decode()

                if expected_ack == "ACK":
                    # Open the file descriptor for receive the song
                    # and write into it
                    f = open(Server.path_of_shared_music + required_song, "wb")

                    while True:
                        try:
                            # Recibir datos del cliente.
                            # print('Recibiendo paquete')
                            input_data = s.recv(1024)
                            if not input_data:
                                break
                            else:
                                f.write(input_data)
                        except error:
                            print("Hubo un error recibiendo el archivo")
                            break

                    f.close()

            s.close()
        sock.close()


if __name__ == '__main__':
    ip, port = '127.0.0.1', 8000
    server = Server(ip, port)
    Thread(target=server.wait_for_search).start()
    Thread(target=server.wait_for_get).start()

