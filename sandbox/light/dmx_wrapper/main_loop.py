import module
from typing import List
import dmx
import time

class Chronometer:
    def __init__(self):
        self.temps_debut = None

    def start(self):
        self.temps_debut = time.time()

    def stop(self):
        timeEllapsed = self.get_time()
        self.temps_debut = None
        return timeEllapsed
        
    def get_time(self):
        if self.temps_debut is not None:
            timeEllapsed = (time.time() - self.temps_debut) * 1000
            return timeEllapsed
        else:
            raise ValueError("Le chronomètre n'est pas démarré.")


def get_transition_0(block)->tuple:
    return block['red'], block['green'], block['blue'], block['white']

def get_transition_1(firstBlock, secondBlock, t:int)->tuple:
    ratio = t/firstBlock['dt']
    r:int = int(firstBlock['red'] + (firstBlock['red'] - secondBlock['red']) * ratio)
    g:int = int(firstBlock['green'] + (firstBlock['green'] - secondBlock['green']) * ratio)
    b:int = int(firstBlock['blue'] + (firstBlock['blue'] - secondBlock['blue']) * ratio)
    w:int = int(firstBlock['white'] + (firstBlock['white'] - secondBlock['white']) * ratio)
    return r, g, b, w

universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("TkinterDisplayer")
nbLights:int = 54
timeStep:int = 30
fileName = "file.yaml"


times:List[int] = [0]*nbLights
lights = [dmx.DMXLight4Slot(address=dmx.light.light_map[i]) for i in range()]
for light in lights:
    universe.add_light(light)

thrd = module.threadQueue(nbLights)
thrd.set_file(fileName)
chrono = Chronometer()
chrono.start()

while(thrd.isActive()):
    currentTime = chrono.get_time()
    for lightId in range(nbLights):
        times[lightId] = times[lightId] + currentTime
        currentBlock = thrd.getBlock(lightId)

        if currentBlock['dt'] >= times[lightId]:
            times[lightId] %= timeStep
            thrd.removeBlock(lightId)
            currentBlock = thrd.getBlock(lightId)

        if currentBlock['Tr'] == 0:
            r,g,b,w = get_transition_0(currentBlock)
            lights[lightId].set_colour(dmx.Color(r,g,b,w))
        elif currentTime['Tr'] == 1:
            r,g,b,w = get_transition_1(currentBlock, thrd.get_next_block(lightId), currentTime)
            lights[lightId].set_colour(dmx.Color(r,g,b,w))      
        

    interface.set_frame(universe.serialise())
    interface.send_update()


thrd.quit()