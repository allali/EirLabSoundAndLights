import threading
from typing import List
import yaml
from queue import Queue
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import dmx
import numpy as np

class YamlReader:
    def __init__(self):
        pass

    def _read_yaml(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = yaml.safe_load(file)
                return data
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise ValueError(f"Error reading YAML file: {e}")
            
    def load_file(self, file_name, player, offset = 0, relativeOffset=False):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        #player.add_new_set()
        for item in data:
            for tram in item["times"]:
                player.add(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"], offset, relativeOffset)
        self.file_name = file_name

#############################################################

class Timer:
    def __init__(self):
        self.startTime = None

    def start(self):
        self.startTime = time.time()

    def stop(self):
        timeEllapsed = self.get_time()
        self.startTime = None
        return timeEllapsed
        
    def get_time(self):
        if self.startTime is not None:
            timeEllapsed = (time.time() - self.startTime) * 1000
            return timeEllapsed
        else:
            raise ValueError("Timer has not been started")


#############################################################
        
class Player_Light:

    def __init__(self, lightId:int, queueMaxSize:int):
        self.isRunning:bool = False
        self.queue = Queue(maxsize=queueMaxSize)
        #self.maxQueueSize = queueMaxSize
        self.mixType = 1
        #self.currentSetId = 0
        self.id:int = lightId
        #self.threadQueues = []
        self.lastBlock = [{'time': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0, 'Tr': 0}]
        self.lastTram = np.array([0,0,0,0])
        self.light = dmx.DMXLight4Slot(address=dmx.light.light_map[lightId])


    def add_to_universe(self, dmxUniverse:dmx.DMXUniverse):
        dmxUniverse.add_light(self.light)

    
    def _mix(self, blocks, currentTime:int):       
        if (len(blocks) == 0):
            return self.lastTram
        res = np.array([0,0,0,0])
        if (self.mixType == 0):
            for queueId in range(len(blocks)):
                tram = self._get_rgbw(blocks, queueId, currentTime)
                res += tram
            res //= len(blocks)
        elif self.mixType == 1:
            for queueId in range(len(blocks)):
                tram = self._get_rgbw(blocks, queueId, currentTime)
                res = np.where(res > tram, res, tram)
        return res

        


    def get_block(self):
        #thQueue = self.threadQueues[threadQueueId]
        if (self.queue.qsize() > 0):  
            return self.queue.queue[0]
        else:
            return self.lastBlock[0]
            #raise Exception("Queue shouldn't be empty")
            
        
    def get_next_block(self, threadQueueId):
        thQueue = self.threadQueues[threadQueueId]
        if (thQueue.qsize() > 1): 
            return thQueue.queue[1]
        else:
            return None
        
    def _clean_queue(self, currentTime:int):
        #if (self.queue.qsize() == 0):
            #self.threadQueues.pop(queueId)
            #self.lastBlock.pop(0)
            #self.currentSetId -= 1
            # if (self.currentSetId == 0):
            #     self.isRunning = False
            #return True
            
        res = self.get_block()
        while(res["time"] < currentTime):
            self.lastBlock = res
            if (self.remove_block()):
                return True
            res = self.get_block()
        return False
    
    def clean_queues(self, currentTime):
        # add = 0
        # for queueId in range(len(self.threadQueues)):
        #     if (self._clean_queue(currentTime, queueId-add)):
        #         add += 1
        self._clean_queue(currentTime)
        
            
        
    
    def remove_block(self):
        self.queue.get()
        if (self.queue.qsize() == 0):
            #self.threadQueues.pop(threadQueueId)
            self.lastBlock.pop(0)
            #self.currentSetId -= 1
            # if (self.currentSetId == 0):
            #     self.isRunning = False
            return True
        elif (self.queue.qsize() == 1 and self.queue.queue[0]['Tr'] != -1):
            endBlock = self.queue.queue[0]
            self.queue.put({"time":endBlock["time"]+50, "red":endBlock["red"], "green":endBlock["green"], "blue":endBlock["blue"], "white":endBlock["white"], "Tr":-1})
        
        return False


    def add(self,time:int, rgbw:List[int], tr:int, offset:int):
        self.isRunning = True
        self.queue.put({"time":time + offset, "red":rgbw[0], "green":rgbw[1], "blue":rgbw[2], "white":rgbw[3], "Tr":tr})     
    
    def _get_current_block(self, currentTime):
        #currentBlocks = []
        self.clean_queues(currentTime)
        # for queueId in range(self.currentSetId):
        #     currentBlocks.append(self.get_block(queueId))

        currentBlock = self.get_block()

        #self.lastTram = self._mix(currentBlock, currentTime)  
        self.lastTram = self._get_rgbw(currentBlock, currentTime)
        return self.lastTram

    

    def _get_rgbw(self, block, currentTime):
        if (block['Tr'] == 0) or (block['Tr'] == -1):
            lastBlock = self.lastBlock[0]
            return np.array([lastBlock['red'],lastBlock['green'],lastBlock['blue'],lastBlock['white']])
        elif block['Tr'] == 1:
            return np.array(self._get_transition_1_rgbw(self.lastBlock[0], block, currentTime))
        else:
            return None, None, None, None
        
    
    def _get_transition_1_rgbw(self, startBlock, endBlock, time):
        ratio = (time - startBlock['time']) / (endBlock["time"] - startBlock['time'])
        ratio = 1 if ratio > 1 else ratio
        r:int = int(startBlock['red'] + (endBlock['red'] - startBlock['red']) * ratio)
        g:int = int(startBlock['green'] + (endBlock['green'] - startBlock['green']) * ratio)
        b:int = int(startBlock['blue'] + (endBlock['blue'] - startBlock['blue']) * ratio)
        w:int = int(startBlock['white'] + (endBlock['white'] - startBlock['white']) * ratio)
        return r,g,b,w
    
    
    def set_color(self, r, g, b, w):
        if r is not None:
            self.light.set_colour(dmx.Color(r,g,b,w))

    # def add_new_set(self):
    #     self.lastBlocks.append({'time': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0, 'Tr': 0})
    #     self.threadQueues.append(Queue(maxsize=self.maxQueueSize))
    #     self.currentSetId += 1

    

#################################################

class Player:

    def __init__(self, nbLights:int, interfaceName:str):
        self.isRunning:bool = False
        self.file_name:str = None
        self.num_lights:int = nbLights

        self.mainThread = threading.Thread(target=self._worker, args=[interfaceName])
        self.timer = Timer()

        self.universe = dmx.DMXUniverse()
        self.lights:List[Player_Light] = []
        for lightId in range(nbLights):
            self.lights.append(Player_Light(lightId, 0))
            self.lights[lightId].add_to_universe(self.universe)
        
                
    def add(self, lightId:int, time:int, rgbw:List[int], tr:int, offset:int, relativeOffset:bool):
        globalOffset = 0
        if (relativeOffset):
            globalOffset = self.timer.get_time()
        
        self.lights[lightId].add(time, rgbw, tr, offset+globalOffset)
        #print("ici",time, rgbw, tr, offset+globalOffset)
        #print(lightId,self.lights[lightId].queue.queue[0])

        #self.thread_queues[lightId].put({"time":time + offset, "id": lightId, "red":rgbw[0], "green":rgbw[1], "blue":rgbw[2], "white":rgbw[3], "Tr":tr})
    
    
    # def add_new_set(self):
    #     for light in self.lights:
    #         light.add_new_set()


    def start(self):
        self.isRunning = True
        self.mainThread.start()

    
    
    def _worker(self, interfaceName):
        # Tkinter windows must be used by one and unique thread. 
        # We must declare this interface in this thread
        self.isRunning = True
        interface = dmx.DMXInterface(interfaceName)
        self.timer.start()
        currentTime = -1
        while(self.isRunning):
            for light in self.lights:
                r, g, b, w = light._get_current_block(currentTime)
                #r, g, b, w = light._get_rgbw(currentBlock, currentTime)
                light.set_color(r,g,b,w)
                print("light", light.id, "is doing", r, g, b, w, "at", currentTime)


            interface.set_frame(self.universe.serialise())
            interface.send_update()
            currentTime = self.timer.get_time()
        
        interface.close()



    def is_running(self):
        for light in self.lights:
            if (light.isRunning):
                return True
            
        return False
    

    def quit(self):
        self.isRunning=False


##################################################

if __name__ == "__main__":
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R"
    player = Player(54, interfaceName)
    yr = YamlReader()
    yr.load_file(r"../yamls/snake2.yml", player, 200)
    # yr.load_file(r"../yamls/snake2.yml", player, 1200)
    # yr.load_file(r"../yamls/snake2.yml", player, 3200)
    # yr.load_file(r"../yamls/snake2.yml", player, 4200)
    #yr.load_file(r"../yamls/sound_10_tracks.yml", player, 0, False)
    player.start()
    while (player.is_running()):
        time.sleep(1)
    player.quit()