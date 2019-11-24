 #THere wi have the tools for nodes
"""import vlc"""


def play_song(song, dir_file):
    p = None
    '''p = vlc.MediaPlayer(dir_file + song)'''
    p.play()
    print("Write \"pause\" for pause the song or press \"enter\" to stop it")

    while p.get_position() != -1.0:
        action = input()
        if action == 'pause':
            p.pause()
            print("The song is paused, write \"play\" to continue with the reproduction or press \"enter\" to stop it")
        if action == 'play':
            p.play()
            print("Write \"pause\" for pause the song or press \"enter\" to stop it")
        if action == '':
            p.stop()
            print("You have stoped the song")
    print("End of the reproduction")

