import time
import sys
import yaml
import os 

sys.path.append("../../client/files/yamls")
sys.path.append("../light/dmx_wrapper")
sys.path.append("../light")
sys.path.append("../sound")

from New_player import YamlReader, Player
from play_file_func import AudioPlayer
from InstrumentsHTH import Instruments

#yaml_generating
yMetaDataFilePath = "./HighwayToHell.yaml"
with open(yMetaDataFilePath, "r") as yfile:
    data = yaml.safe_load(yfile)

MetaYaml = data[1]
tags = []
#keys = list(MetaYaml["parts"].keys())

for part in MetaYaml["parts"]:
    #print(part)
    tags.append((part["time"],part["type"],part["tag"]))

os.remove("../../client/files/yamls/HTH.yaml")
newYml = Instruments("HTH")
for (timing,type,list) in tags:
    if type == "build":
        newYml.build(timing*1000)
    elif type == "intro":
        for instrument in list:
            if instrument == "guitar1":
                newYml.guitar(timing*1000)
            if instrument == "drums1" and timing < 9.44:
                for i in range(13):
                    newYml.drums((timing+ i)*1000 )
    elif type == "verse":
        for k in range(4):
            for instrument in list:
                if instrument == "guitar1":
                    newYml.guitar(timing*1000 + k * 8400)
                if instrument == "drums1":
                    for i in range(13):
                        newYml.drums((timing+ i)*1000 + k * 8400 )                   
    elif type == "chorus":
        for instrument in list:
            if instrument == "drums2":
                newYml.random_period(timing*1000,250,3)
            if instrument == "guitar2":
                newYml.full_change(timing*1000)

newYml.write()


#ligth
nbLights = 54
interfaceName = "TkinterDisplayer"
LigthPlayer = Player(54,interfaceName)
yr = YamlReader()
yr.load_file(newYml.ymlFile.file_path,LigthPlayer)


#sound
#SoundFilePath = "../sound/10tracks_studio/10_HTH.wav"
#audioPlayer = AudioPlayer("HTH",20)
#audioPlayer.load_file(SoundFilePath)    

#start
LigthPlayer.start()
time.sleep(1)
#audioPlayer.start()

    

LigthPlayer.quit()
