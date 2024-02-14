import time
import sys
sys.path.append("./light/dmx_wrapper")
sys.path.append("./light")
sys.path.append("./sound")

from Player import YamlReader, Player
from play_file_func import AudioPlayer


nbLights = 54
interfaceName = "TkinterDisplayer" # "FT232R"
player = Player(54, interfaceName)
yr = YamlReader()
# yr.load_file(r"../yamls/snake2.yml", player, 200)
# yr.load_file(r"../yamls/snake2.yml", player, 1200)
# yr.load_file(r"../yamls/snake2.yml", player, 3200)
# yr.load_file(r"../yamls/snake2.yml", player, 4200)
yr.load_file(r"./light/yamls/sound_10_tracks.yml", player, 0, False)

audioPlayer = AudioPlayer()
audioPlayer.load_file(r"./sound/10tracks_studio/test_10_pistes_metronome.wav")

audioPlayer.start()
player.start()
while (player.is_running()):
    time.sleep(1)
player.quit()