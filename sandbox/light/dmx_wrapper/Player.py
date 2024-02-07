import threading
import yaml
from queue import Queue
import time
import sys
sys.path.append("..")
import dmx

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
            
    def play_file(self, file_name, player, offset = 0):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")

        for item in data:
            for tram in item["times"]:
                player.add(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"], offset)
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

class Player:
    def __init__(self, nbLights, interfaceName):
        self.file_name = None
        self.num_lights = nbLights
        self.isRunning = False
        self.thread_queues = [Queue(maxsize=0) for _ in range(nbLights)]
        self.lastBlock = [{'time': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0, 'Tr': 0}] * nbLights
        self.mainThread = threading.Thread(target=self._worker, args=[interfaceName])
        self.timer = Timer()
        self.universe = dmx.DMXUniverse()
        self.lights = [dmx.DMXLight4Slot(address=dmx.light.light_map[i]) for i in range(nbLights)]
        for light in self.lights:
            self.universe.add_light(light)
        
        

        
    def add(self, lightId, time, rgbw, tr, offset):
        self.thread_queues[lightId].put({"time":time + offset, "id": lightId, "red":rgbw[0], "green":rgbw[1], "blue":rgbw[2], "white":rgbw[3], "Tr":tr})


    def start(self):
        self.isRunning = True
        self.mainThread.start()

    
    def _get_transition_1_rgbw(self, startBlock, endBlock, time):
        ratio = (time - startBlock['time']) / (endBlock["time"] - startBlock['time'])
        ratio = 1 if ratio > 1 else ratio
        r:int = int(startBlock['red'] + (endBlock['red'] - startBlock['red']) * ratio)
        g:int = int(startBlock['green'] + (endBlock['green'] - startBlock['green']) * ratio)
        b:int = int(startBlock['blue'] + (endBlock['blue'] - startBlock['blue']) * ratio)
        w:int = int(startBlock['white'] + (endBlock['white'] - startBlock['white']) * ratio)
        return r,g,b,w
    
    def _get_current_block(self, lightId, currentTime):
        currentBlock = self.get_block(lightId)
        nextBlock = self.get_next_block(lightId)
        
        if ((currentBlock['time'] <= currentTime and nextBlock['Tr'] in [1,-1] ) or (nextBlock['time'] <= currentTime and nextBlock['Tr'] == 0)):
            self.lastBlock[lightId] = currentBlock
            self.remove_block(lightId)
            return self.get_block(lightId)
        
        return currentBlock
    
    def _get_rgbw(self, block, lightId, currentTime):
        if block['Tr'] == 0:
            return block['red'],block['green'],block['blue'],block['white']
        elif block['Tr'] == 1:
            return self._get_transition_1_rgbw(self.lastBlock[lightId], block, currentTime)
        else:
            return None, None, None, None
            
    
    def _worker(self, interfaceName):
        # Tkinter windows must be used by one and unique thread. 
        # We must declare this interface in this thread
        interface = dmx.DMXInterface(interfaceName)
        self.isRunning = True
        self.timer.start()
        currentTime = -1
        while(self.isRunning):
            for lightId, light in enumerate(self.lights):
                currentBlock = self._get_current_block(lightId, currentTime)
                r, g, b, w = self._get_rgbw(currentBlock, lightId, currentTime)
                if r is not None:
                    light.set_colour(dmx.Color(r,g,b,w))

            interface.set_frame(self.universe.serialise())
            interface.send_update()
            currentTime = self.timer.get_time()

        interface.close()


    def get_block(self, light_id):  
        if 0 <= light_id < self.num_lights:
            if (self.thread_queues[light_id].qsize() > 0):     
                return self.thread_queues[light_id].queue[0]
            else:
                return {'time': self.timer.get_time(), 'red': 0, 'green': 0, 'blue': 0, 'white': 0, 'Tr': -1}
        else:
            raise Exception(f"Wrong light id in get_block. Given id : {light_id}")

    def get_next_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            if (self.thread_queues[light_id].qsize() > 1): 
                return self.thread_queues[light_id].queue[1]
            else:
                return {'time': self.timer.get_time(), 'red': 255, 'green': 255, 'blue': 255, 'white': 200, 'Tr': -1}
        else:
            raise Exception(f"Wrong light id in get_block. Given id : {light_id}")

    def remove_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            self.thread_queues[light_id].get()

    def is_running(self):
        if (not(self.isRunning)):
            return False
        for lightId in range(self.num_lights):
            if self.thread_queues[lightId].qsize() != 0:
                return True
            #print(self.thread_queues[lightId].qsize())
            
        return False

    def quit(self):
        self.isRunning=False




if __name__ == "__main__":
    nbLights = 54
    interfaceName = "TkinterDisplayer"
    player = Player(54, interfaceName)
    yr = YamlReader()
    yr.play_file(r"../yamls/snake2.yml", player, 2000)
    player.start()
    while (player.is_running()):
        time.sleep(1)
    player.quit()