import time
import os
import argparse
from typing import List

from light.yaml_manager import YamlReader, YamlWritter
from light.lightsPlayer import LightsPlayer
from light.StaticLightPlayer import StaticLightsPlayer
from sound.audioPlayer import AudioPlayer
from light.frame import MergeType, OffsetType

class Player:
    
    def __init__(self):
        self.lightPlayer = None
        self.nbLights = None
        self.lightInterface = None
        self.yamlReader = None
        self.isPlayerDynamic = None
        
        self.audioPlayer = None
        self.audioClientName = None
        self.audioBufferSize = None
        
    def init_audio(self, clientName:str, bufferSize:int):
        if (self.audioPlayer is not None):
            raise ValueError("Audio player has already been initialized")
        self.audioClientName = clientName
        self.audioBufferSize = bufferSize
        self.audioPlayer = AudioPlayer(self.audioClientName, self.audioBufferSize)
        
    def init_light(self, nbLights:int, interfaceName:str, isPlayerDynamic:bool):
        if (self.lightPlayer is not None):
            raise ValueError("Light player has already been initialized")
        self.nbLights = nbLights
        self.lightInterface = interfaceName
        self.isPlayerDynamic = isPlayerDynamic
        self.lightPlayer = LightsPlayer(self.nbLights, self.lightInterface) if isPlayerDynamic else StaticLightsPlayer(self.nbLights, self.lightInterface)
        
    def load_audio_file(self, audioFile:str):
        if (self.audioPlayer is None):
            raise ValueError("AudioPlayer has not been initialized")
        self.audioPlayer.load_file(audioFile)
        
    def load_yaml(self, yamlFiles:str | List[str], mergeType:MergeType):
        if (self.lightPlayer is None):
            raise ValueError("LightsPlayer has not been initialized")    
        if (self.isPlayerDynamic):
            for yamlFile in yamlFiles:
                YamlReader.load_file(yamlFile, self.lightPlayer, 0, False)
        else:
            YamlWritter.merge_yamls(yamlFiles, "__tmpYaml__.yaml", self.nbLights, mergeType)
            frame = YamlReader.file_to_frame("__tmpYaml__.yaml", 54)
            frame.push(self.lightPlayer, mergeType, OffsetType.ABSOLUTE, 0)
            os.remove("__tmpYaml__.yaml")
    
    def start(self):
        if (self.audioPlayer is not None):
            self.audioPlayer.start()
        if (self.lightPlayer is not None):
            self.lightPlayer.start()
    
    def quit(self):
        if (self.audioPlayer is not None):
            self.audioPlayer.quit()
        if (self.lightPlayer is not None):
            self.lightPlayer.quit()
        
    def is_running(self):
        if self.audioPlayer is not None and self.audioPlayer.is_running():
            return True
        elif self.lightPlayer is not None and self.lightPlayer.is_running():
            return True
        return False
        
        
        

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dynamic', action="store_true", help='Use dynamic light player version')
parser.add_argument('-s', '--soundFile', type=str, default=None, help='audio file to be played back')
parser.add_argument('-y', '--yaml', type=str, default=None, help='Yaml file to be played by lights', nargs="+")
parser.add_argument('--merge', type=str, default="MAX", help='Merge type if multiple yamls and static player')
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
    
mergeType = MergeType.MAX
match args.merge:
    case "MAX":
        mergeType = MergeType.MAX
    case "MIN":
        mergeType = MergeType.MIN
    case "MEAN":
        mergeType = MergeType.MEAN

nbLights = 54
player = Player()


if (args.yaml is not None):
    player.init_light(54, args.interface, args.dynamic) # FT232R TkinterDisplayer
    player.load_yaml(args.yaml, mergeType)
    
    
if (args.soundFile is not None):
    player.init_audio(args.clientname, args.buffersize)
    player.load_audio_file(args.soundFile)

player.start()

while (player.is_running()):
    time.sleep(1)
    if (args.loop):
        pass # Do the loop if needed
player.quit()