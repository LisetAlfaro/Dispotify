# THere we have the tools for nodes
import os
import socket
from socket import error
from typing import Dict, Any, Union, Tuple
import selectors
import sys
import vlc
from mutagen.easyid3 import EasyID3
import Pyro4


def timed_input(time_out=4):
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ, input)
    answer = None
    event = selector.select(timeout=time_out)
    if event:
        answer = input()
    return answer


def play_song(song, dir_file):
    p = vlc.MediaPlayer(dir_file + song)
    p.play()
    print("Write \"pause\" for pause the song or press \"enter\" to stop it")
    playing = set([5, 6])
    while True:
        if p.get_state() in playing:
            break
        action = timed_input()
        if action == 'pause':
            p.pause()
            print("The song is paused, write \"play\" to continue with the reproduction or press \"enter\" to "
                  "stop it")
        if action == 'play':
            p.play()
            print("Write \"pause\" for pause the song or press \"enter\" to stop it")
        if action == '':
            p.stop()
            print("You have stopped the song")
            break
    print("End of the reproduction")
    return


def get_dir_size(the_path):
    """Get size of a directory tree in bytes."""
    path_size = 0
    for path, dirs, files in os.walk(the_path):
        for fil in files:
            filename = os.path.join(path, fil)
            path_size += os.path.getsize(filename)
    return path_size


def get_uri_from_ip_and_port(type_of_node, ip, port):
    uri = 'PYRO:' + type_of_node + '@' + str(ip) + ':' + str(port)
    return uri


def get_ip_and_port_from_uri(uri):
    double_dots_index = uri.find(':')
    sub_uri = uri[double_dots_index + 1:]
    double_dots_index = sub_uri.find(':')
    arroba_index = sub_uri.find('@')
    ip = sub_uri[arroba_index + 1 :double_dots_index]
    port = sub_uri[double_dots_index + 1 :]
    return ip, port


def do_broadcast(ip: object, self_port: object, self_uri: object) -> object:
    # Initialize list_uri
    list_uri = []
    # Sending broadcast
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    # server.set timeout(0.2)

    try :
        client.bind((ip, self_port + 2000))
    except OSError :
        return
    message = b"valarmorghulis"

    for inc in range(1000):
        client.sendto(message, ('<broadcast>', 12000 + inc))

    client.close()

    # Then we listen in a TCP socket
    # Listening response
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set timeout
    try :
        client.bind((ip, self_port + 2000))
    except OSError :
        return
    client.settimeout(0.5)
    client.listen(1000)
    # Fill list_uir with the responses
    while True :
        try :
            s, addr_info = client.accept()
            s_uri = s.recv(1024).decode()
            if s_uri != '' :
                list_uri.append(s_uri)
        except socket.timeout :
            break
    if self_uri not in list_uri :
        list_uri.append(self_uri)

    return list_uri


def get_song_for_search(attribute, attribute_name, uri):
    # Get ip and port from the current uri
    ip, port = get_ip_and_port_from_uri(uri)

    # I establish a TCP connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port) + 2000))
    except (ConnectionRefusedError, OSError):
        return

    # Send Search request
    data = 'SEARCH' + ' ' + str(attribute) + ' ' + attribute_name
    try:
        s.send(data.encode())

    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
            OSError):
        return False
    if attribute == 1:
        data = s.recv(3)
        if data.decode() == 'Yes':
            return "Yes"

    else:
        list_music = []
        while True:
            data = s.recv(1024)
            if data.decode() == "ALD":
                break
            list_music.append(str(data.decode()))
        s.close()
        return list_music


def get_song_from_uri(selected_song, server_uri):
    """
    Create an archive with the song received from the node with the gived uri
    Params:
    song: The song to obtain
    server_uri: The uri where the song is located
    uri: The uri whose wants the song
    """

    # Get ip and port from the current uri
    ip, port = get_ip_and_port_from_uri(server_uri)

    # I establish a TCP connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port) + 1000))
    except (ConnectionRefusedError, OSError):
        return
    # Send GET request
    data = 'GET' + ' ' + selected_song

    try:
        s.send(data.encode())
    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
            OSError):
        return False

    raw_recv_data = s.recv(len("ValarMorghulis"))
    recv_data = raw_recv_data.decode()

    if recv_data == "ValarMorghulis":

        data = 'ValarDohaeris:'

        try:
            s.send(data.encode())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
                OSError):
            return False

        # Open the file descriptor for receive the song
        # and write into it
        f = open(selected_song, "wb")

        while True:
            try:
                # Get data from server.

                input_data = s.recv(1024)

                if not input_data:
                    print("The song has been received correctly")
                    f.close()
                    s.close()
                    return True
                else:

                    f.write(input_data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError,
                    ConnectionRefusedError, OSError):
                print("An error has occurred receiving the song")
                f.close()
                os.remove(selected_song)
                s.close()
                return False

        f.close()

    else:
        print("The protocol has failed")
    s.close()


def waiting_to_broadcast(self_port, self_uri):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(('', self_port + 4000))

    while True :
        data, addr = client.recvfrom(len("VALARMORGHULIS"))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True :
            try :
                sock.connect((addr[0], addr[1]))
                break
            except (ConnectionRefusedError, OSError) :
                print("Can't connect to " + str((addr[0], addr[1])))
                continue
        try :
            sock.send(str(self_uri).encode())
        except (
        BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError) :
            continue

    client.close()


if __name__ == '__main__':
    get_song_for_search(1,"a.mp3","PYRO:server@127.0.0.1:8000")
