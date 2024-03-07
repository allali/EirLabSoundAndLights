import time
import sys

sys.path.append("./sound")

from play_file_func import AudioPlayer

buffsize = 20 
audioFile = "./sound/10tracks_studio/test_10_pistes.wav"
clientName = "test_sound"

audioPlayer = AudioPlayer(clientName, buffsize)

audioPlayer.load_file(audioFile)

audioPlayer.start()

