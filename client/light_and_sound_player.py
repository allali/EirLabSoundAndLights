import time
import sys
import argparse
sys.path.append("./light")
sys.path.append("./yamls")
sys.path.append("./sound")
sys.path.append("./audio_files/10tracks_studio")

from Player import YamlReader, Player
from play_file_func import AudioPlayer

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-s', '--soundFile', type=str, default=None, help='audio file to be played back')
parser.add_argument('-y', '--yaml', type=str, default=None, help='Yaml file to be use for lights')
parser.add_argument('-i', '--interface', type=str, default="TkinterDisplayer", help='Visual interface')
parser.add_argument('--loop', action='store_true', default=False, help='Repeat')
parser.add_argument(
    '-b', '--buffersize', type=int, default=20,
    help='number of blocks used for buffering (default: %(default)s)')
parser.add_argument('-c', '--clientname', default='file player',
                    help='JACK client name')
parser.add_argument('-m', '--manual', action='store_true',
                    help="don't connect to output ports automatically")
args = parser.parse_args()
print(args)
    


nbLights = 54
interfaceName = args.interface # "FT232R"
yamlFile = args.yaml # r"./light/yamls/sound_10_tracks.yml"
audioFile = args.soundFile # r"./sound/10tracks_studio/test_10_pistes_metronome.wav"

player = Player(54, interfaceName)
yr = YamlReader()

if (yamlFile is not None):
    yr.load_file(yamlFile, player, 0, False)
audioPlayer = AudioPlayer(args.clientname, args.buffersize)
if (audioFile is not None):
    audioPlayer.load_file(audioFile)
player.start()
audioPlayer.start()

while (player.is_running()):
    time.sleep(1)
    if (args.loop):
        pass # Do the loop if needed
player.quit()