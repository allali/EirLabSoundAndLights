import time
import sys

sys.path.append("./light/dmx_wrapper")
sys.path.append("./light")
sys.path.append("./sound")

from play_file_func import AudioPlayer
from New_player import YamlReader, Player


buffsize = 20 
audioFile = "./sound/10tracks_studio/test_10_pistes_metronome.wav"
clientName = "test_sound"


nbLights = 54
interfaceName = "TkinterDisplayer" # "FT232R" "TkinterDisplayer"

player = Player(nbLights, interfaceName)

yr = YamlReader()
yr.load_file(r"./light/yamls/test.yaml", player)

id_lights = [51,47,29,11,2,6,18,30,42,49]

audioPlayer = AudioPlayer(clientName, buffsize)

audioPlayer.load_file(audioFile)
audioPlayer.start()

time_intervall = 250
current_time = 0

player.start()
old_rms_values = {}
old_red_values = {}

while (player.is_running()):
    for i in range(10):
        x = audioPlayer.get_Rms_Values(i)
        if (x != None):
            if i not in old_red_values.keys():
                old_rms_values[i] = x 
                player.add(id_lights[i], current_time + time_intervall, [255,0,0,0],0,0)
                old_red_values[i] = 255

            else :
                delta = x/old_rms_values.get(i)
                old_rms_values[i] = x 

                new_rgb_value = old_red_values.get(i)*(1 - delta)
                player.add(id_lights[i],current_time + time_intervall, [new_rgb_value,0,0,0],0,0)

                old_red_values[i] = new_rgb_value

    current_time += time_intervall

player.quit()


