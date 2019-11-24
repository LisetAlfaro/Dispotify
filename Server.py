"""this is a distributed server, here are the functions to connect with other servers and serve clients"""
import socket
from socket import error

"""Here is the Chord implementation"""


class Server:

    def __init__(self):
        self.ip
        self.port
        self.my_music = {}
        self.my_music_folder_path

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

            # if data[:4] == 'PUSH':
            #     required_song = data[5:]
            #
            #     # If I can receive the song I send ACK
            #     s.send(b"ACK")
            #
            #     # Finishing handshake
            #     expected_ack = s.recv(3).decode()
            #
            #     if expected_ack == "ACK":
            #         # Open the file descriptor for receive the song
            #         # and write into it
            #         f = open(Server.path_of_shared_music + required_song, "wb")
            #
            #         while True:
            #             try:
            #                 # Recibir datos del cliente.
            #                 # print('Recibiendo paquete')
            #                 input_data = s.recv(1024)
            #                 if not input_data:
            #                     break
            #                 else:
            #                     f.write(input_data)
            #             except error:
            #                 print("Hubo un error recibiendo el archivo")
            #                 break
            #
            #         f.close()
            #
            # s.close()
        sock.close()
