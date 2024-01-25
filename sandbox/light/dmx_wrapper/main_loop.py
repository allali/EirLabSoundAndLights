import LightController
from typing import List
import sys
sys.path.append("..")
import os
import dmx
import time
import LightController

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
    
    def slice_time(self):
        if self.temps_debut is not None:
            timeEllapsed = (time.time() - self.temps_debut) * 1000
            self.temps_debut = time.time()
            return timeEllapsed
        else:
            raise ValueError("Le chronomètre n'est pas démarré.")


def get_transition_0(block)->tuple:
    return block['red'], block['green'], block['blue'], block['white']

def get_transition_1(firstBlock, secondBlock, t:int)->tuple:
    ratio = (1. * t)/firstBlock['dt']
    r:int = int(firstBlock['red'] + (secondBlock['red'] - firstBlock['red']) * ratio)
    g:int = int(firstBlock['green'] + (secondBlock['green'] - firstBlock['green']) * ratio)
    b:int = int(firstBlock['blue'] + (secondBlock['blue'] - firstBlock['blue']) * ratio)
    w:int = int(firstBlock['white'] + (secondBlock['white'] - firstBlock['white']) * ratio)
    return r, g, b, w

universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("TkinterDisplayer")
nbLights:int = 54
timeStep:int = 30
fileName = r"../yamls/snake.yml"


times:List[int] = [0]*nbLights
lights = [dmx.DMXLight4Slot(address=dmx.light.light_map[i]) for i in range(nbLights)]
for light in lights:
    universe.add_light(light)

thrd = LightController.LightController(nbLights)
thrd.set_file(fileName)
chrono = Chronometer()
chrono.start()

while(thrd.is_active()):
    currentTime = chrono.slice_time()
    for lightId in range(nbLights):
        times[lightId] = times[lightId] + currentTime
        currentBlock = thrd.get_block(lightId)

        if currentBlock['dt'] <= times[lightId] and currentBlock['dt'] != -1:
            times[lightId] %= timeStep
            thrd.remove_block(lightId)
            currentBlock = thrd.get_block(lightId)
        if currentBlock['Tr'] == 0:
            r,g,b,w = get_transition_0(currentBlock)
            lights[lightId].set_colour(dmx.Color(r,g,b,w))
        elif currentBlock['Tr'] == 1:
            r,g,b,w = get_transition_1(currentBlock, thrd.get_next_block(lightId), times[lightId])
            lights[lightId].set_colour(dmx.Color(r,g,b,w))      
        

    interface.set_frame(universe.serialise())
    interface.send_update()


thrd.quit()