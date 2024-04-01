import threading
from typing import List
import yaml
import queue
import time
import sys
sys.path.append("..")
import dmx
import numpy as np
FREQUENCY = 27

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
    
    def load_file(self, file_name, player, offset = 0):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        player.added_file_names.append(file_name)
        for item in data:
            for tram in item["times"]:
                player.add(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"], offset)
        
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
        
class SingleLightQueue:
    def __init__(self, lightId:int, queueMaxSize:int):
        self.lightId:id = lightId
        self.queue = queue.PriorityQueue(maxsize=queueMaxSize)
        self.light = dmx.DMXLight4Slot(address=dmx.light.light_map[lightId])
        self.isRunning:bool = True
        self.no_event = np.array([0,0,0,0])
        self.current_event = None
        self.next_event = None
        self.transition_step_size = 0
        self.transition_progress = 0

    def add_to_universe(self, dmxUniverse:dmx.DMXUniverse):
        dmxUniverse.add_light(self.light)

    
    def get_next_event(self):
        if not self.queue.empty():
            return self.queue.queue[0]
        return None
    
    def adjust_time(self, time:int):
        return time + (FREQUENCY - time % FREQUENCY) % FREQUENCY

    def fill_queue(self, time:int, rgbw:List[int], Tr:int):
        time = self.adjust_time(time)
        self.add(time, rgbw, Tr)

    def add(self, time:int, rgbw:List[int], Tr:int):
        self.queue.put((time, rgbw, Tr), block=False)
        
    # def create_transition(self, previous_event, current_event):
    #     time, rgbw, Tr = current_event
    #     previous_time, previous_rgbw, previous_Tr = previous_event

    #     number_of_steps = (time - previous_time) // FREQUENCY
    #     step_size = [(current - previous) / number_of_steps for current, previous in zip(rgbw, previous_rgbw)]
    #     print("step_size",step_size)
    #     for i in range(1, number_of_steps):  
    #         transition_rgbw = [int(previous + step * i) for previous, step in zip(previous_rgbw, step_size)]
    #         self.add(previous_time + i * FREQUENCY, transition_rgbw, 0)
    
    def set_color(self, rgbw:List[int]):
        self.light.set_colour(dmx.Color(rgbw[0], rgbw[1], rgbw[2], rgbw[3]))

    def set_next_event(self, timeEllapsed:int):
        if self.queue.empty():
            self.isRunning = False
            return 
        self.next_event = self.get_next_event()

        if self.next_event is not None:
            event_time, event_rgbw, event_type = self.next_event

            if abs(self.next_event[0] - timeEllapsed) < FREQUENCY:
                self.current_event = self.next_event
                self.transition_progress = 0
                self.remove_event()
                self.set_color(event_rgbw)
                self.isRunning = True
                return 
            
            if event_type == 0:
                self.transition_step_size = 0
                self.transition_progress = 0

            if event_type == 1 and self.current_event:
                if self.current_event[2] == 1:
                    self.add(self.current_event[0], self.current_event[1], 0)
                else:
                    previous_time, previous_rgbw, _ = self.current_event
                    total_steps = (event_time - previous_time) // FREQUENCY
        
                    if self.transition_progress >= total_steps:
                        return
                    self.transition_progress = abs((timeEllapsed - previous_time) / FREQUENCY)

                    step_size = [(current - previous) / total_steps for current, previous in zip(event_rgbw, previous_rgbw)]
                    transition_rgbw = [int(previous + (step * self.transition_progress)) for previous, step in zip(previous_rgbw, step_size)]
                    self.set_color(transition_rgbw)


        while self.next_event is not None and timeEllapsed > self.next_event[0]:
            self.next_event = self.get_next_event()
            self.remove_event()

            
    def remove_event(self):
        self.queue.get()

        
#################################################

class Player:
    def __init__(self, nbLights:int, interfaceName:str):
        self.added_file_names:List[str] = []
        self.timer = Timer()
        self.time_debug = Timer()
        self.universe = dmx.DMXUniverse()
        self.interface_name = interfaceName

        self.nbLights:int = nbLights
        self.lights = [SingleLightQueue(i, 0) for i in range(nbLights)]
        self._add_lights_to_universe()

        self.mainThread = threading.Thread(target=self._worker, args=[interfaceName])
        self.isRunning:bool = False

    def _add_lights_to_universe(self):
        for light in self.lights:
            light.add_to_universe(self.universe)

    def add(self, lightId:int, time:int, rgbw:List[int], Tr:int, offset:int):
        time += offset
        self.lights[lightId].fill_queue(time, rgbw, Tr)

    def start(self):
        self.isRunning = True
        self.mainThread.start()
    
    def quit(self):
        self.isRunning = False
        self.mainThread.join()
        #à voir pour que ça exit direct et pas que ça attende la fin de la boucle

    def is_running(self):
        for light in self.lights:
            if light.isRunning:
                return True

    def _worker(self, interfaceName:str):
        self.isRunning = True
        timeEllapsed = -1
        interface = dmx.DMXInterface(interfaceName)
        self.timer.start()
        print("sarting")
        while (self.isRunning):
            for light in self.lights:
                light.set_next_event(timeEllapsed)
            interface.set_frame(self.universe.serialise())
            interface.send_update()
            self.isRunning = self.is_running()
            timeEllapsed = self.timer.get_time()

        self.timer.stop()
        interface.close()
    

##################################################

if __name__ == "__main__":
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R",TkinterDisplayer,Dummy
    player = Player(54, interfaceName)
    yr = YamlReader()
    yr.load_file(r"../yamls/snake2.yml", player)
    yr.load_file(r"../yamls/snake2.yml", player, 200)
    for light in player.lights:
        print(light.queue.queue)
    player.start()
    while (player.isRunning):
        time.sleep(1)
    player.quit()