import time
import sys
import argparse

sys.path.append("./sound")

from play_file_func import AudioPlayer

buffsize = 20 
audioFile = "./sound/10tracks_studio/universal_10_pistes.wav"
clientName = "test_sound"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-m","--map")
parser.add_argument("-l","--loop",action="store_true")
args = parser.parse_args()



audioPlayer = AudioPlayer(clientName, buffsize)

audioPlayer.load_file(audioFile)

if (args.map != None):
    audioPlayer.manual = args.map

audioPlayer.loop = args.loop

audioPlayer.start()

