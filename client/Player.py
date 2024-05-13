import time
import argparse

from light.lightsPlayer import YamlReader, LightsPlayer
from sound.audioPlayer import AudioPlayer

class Player:
    
    def __init__(self):
        self.lightPlayer = None
        self.nbLights = None
        self.lightInterface = None
        self.yamlReader = None
        
        self.audioPlayer = None
        self.audioClientName = None
        self.audioBufferSize = None
        
    def init_audio(self, clientName, bufferSize):
        if (self.audioPlayer is not None):
            raise ValueError("Audio player has already been initialized")
        self.audioClientName = clientName
        self.audioBufferSize = bufferSize
        self.audioPlayer = AudioPlayer(self.audioClientName, self.audioBufferSize)
        
    def init_light(self, nbLights, interfaceName):
        if (self.lightPlayer is not None):
            raise ValueError("Light player has already been initialized")
        self.nbLights = nbLights
        self.lightInterface = interfaceName
        self.lightPlayer = LightsPlayer(self.nbLights, self.lightInterface)
        
    def load_audio_file(self, audioFile):
        if (self.audioPlayer is None):
            raise ValueError("AudioPlayer has not been initialized")
        self.audioPlayer.load_file(audioFile)
        
    def load_yaml(self, yamlFile):
        if (self.lightPlayer is None):
            raise ValueError("LightsPlayer has not been initialized")    
        if self.yamlReader is None:
            self.yamlReader = YamlReader() 
        self.yamlReader.load_file(yamlFile, self.lightPlayer, 0, False)
    
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
parser.add_argument('-s', '--soundFile', type=str, default=None, help='audio file to be played back')
parser.add_argument('-y', '--yaml', type=str, default=None, help='Yaml file to be played by lights', nargs="+")
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
    


nbLights = 54
player = Player()


if (args.yaml is not None):
    player.init_light(54, args.interface) # FT232R TkinterDisplayer
    player.load_yaml(args.yaml)
    
    
if (args.soundFile is not None):
    player.init_audio(args.clientname, args.buffersize)
    player.load_audio_file(args.soundFile)

player.start()

while (player.is_running()):
    time.sleep(1)
    if (args.loop):
        pass # Do the loop if needed
player.quit()