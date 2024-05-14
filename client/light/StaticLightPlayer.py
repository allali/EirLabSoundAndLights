import threading
from typing import List
from collections import deque
from enum import Enum
import time
import sys
import os
filePath = os.path.dirname(__file__)
baseDirIdx = filePath.rfind("/")
sys.path.append("".join(filePath[:baseDirIdx]))
from config import AUDIO_DIR, PARENT_DIR
import dmx
FREQUENCY:int = 27


        
##############################################################
###################         TIMER         ####################
##############################################################

class Timer:
    def __init__(self):
        self.startTime = None

    def start(self) -> None:
        self.startTime = time.time()

    def stop(self) -> float:
        timeEllapsed = self.get_time()
        self.startTime = None
        return timeEllapsed
        
    def get_time(self) -> float:
        if self.startTime is not None:
            timeEllapsed = (time.time() - self.startTime) * 1000
            return timeEllapsed
        else:
            return 0
            raise ValueError("Timer has not been started")
        
        
        
##############################################################
############         SINGLE LIGHT PLAYER         #############
##############################################################
        

        
class SingleLightQueue:
    def __init__(self, lightId:int, queueMaxSize:int | None):
        self.lightId:int = lightId
        self.queue = deque([], queueMaxSize)
        self.history = deque([], None)
        self.light = dmx.DMXLight4Slot(address=dmx.light.light_map[lightId])
        self.isRunning:bool = True
        self.current_event = None
        self.next_event = None
        self.transition_step_size = 0
        self.transition_progress = 0
        self.lastUpdateTime = 0
        self.LastTransition_rgbw = [0,0,0,0]
        self.mutex = threading.Lock()
        

    def add_to_universe(self, dmxUniverse:dmx.DMXUniverse) -> None:
        dmxUniverse.add_light(self.light)

    def loop_refill(self):
        self.queue.extend(self.history)
        self.history.clear()
            
    
    def get_next_event(self) -> List[int] | None:
        if len(self.queue) != 0:
            return self.queue[0]
        return None

    def add(self, time:int, rgbw:List[int], Tr:int) -> bool:
        self.mutex.acquire() # To safely get elmt at index -1 without out of range error
        if (len(self.queue) == 0 or time > self.queue[-1][0]): 
            self.mutex.release()
            self.queue.append((time, rgbw, Tr))
            return True
        self.mutex.release()
        print("Add failed", time, self.queue[-1][0])
        return False
      
        
                
    def set_color(self, rgbw:List[int] | None) -> None:
        self.light.set_color(dmx.Color(rgbw[0], rgbw[1], rgbw[2], rgbw[3]))

    def set_next_event(self, timeEllapsed:int) -> None:
        self.lastUpdateTime = timeEllapsed
        if len(self.queue) == 0:
            self.isRunning = False
            return False
        else:
            self.isRunning = True
        self.next_event = self.get_next_event()

        if self.next_event is not None:
            event_time, event_rgbw, event_type = self.next_event

            if self.next_event[0] - timeEllapsed < FREQUENCY:
                self.current_event = self.next_event
                self.transition_progress = 0
                self.remove_event()
                self.set_color(event_rgbw)
                self.LastTransition_rgbw = event_rgbw
                self.isRunning = True
                return True
            
            if event_type == 0:
                self.transition_step_size = 0
                self.transition_progress = 0

            if event_type == 1 and self.current_event:
            
                previous_time, previous_rgbw, _ = self.current_event
                total_steps = (event_time - previous_time) // FREQUENCY
    
                if self.transition_progress >= total_steps:
                    return True
                self.transition_progress = abs((timeEllapsed - previous_time) / FREQUENCY)

                step_size = [(current - previous) / total_steps for current, previous in zip(event_rgbw, previous_rgbw)]
                self.LastTransition_rgbw = [int(previous + (step * self.transition_progress)) for previous, step in zip(previous_rgbw, step_size)]
                self.set_color(self.LastTransition_rgbw)

        if self.next_event is not None and timeEllapsed > self.next_event[0]:
            self.set_color(self.next_event[1])
            self.next_event = self.get_next_event()
            self.remove_event()
        return True

            
    def remove_event(self) -> None:
        self.mutex.acquire()
        elmt = self.queue.popleft()
        self.mutex.release()
        self.history.append(elmt)
             
        

        
##############################################################
###############         LIGHT PLAYER         #################
##############################################################

class StaticLightsPlayer:
    def __init__(self, nbLights:int, interfaceName:str, isLoopActive:bool=False):
        self.timer:Timer = Timer()
        self.time_debug:Timer = Timer()
        self.universe:dmx.DMXUniverse = dmx.DMXUniverse()
        self.interface_name:str = interfaceName
        self._isRunning = False

        self.nbLights:int = nbLights
        self.lights:List[SingleLightQueue] = [SingleLightQueue(i, None) for i in range(nbLights)]
        self._add_lights_to_universe()

        self.mainThread = threading.Thread(target=self._worker, args=[interfaceName])
        self.isRunning:bool = False
        self.isLoopActive = isLoopActive
        self.refillMutex = threading.Lock()

    def _add_lights_to_universe(self) -> None:
        for light in self.lights:
            light.add_to_universe(self.universe)
            
    def add(self, lightId:int, time:int, rgbw:List[int], Tr:int, offset:int) -> None:
        self.refillMutex.acquire()
        self.lights[lightId].add(time+offset, rgbw, Tr)
        self.refillMutex.release()
        
    def start(self) -> None:
        self.isRunning = True

        self.mainThread.start()
    
    def quit(self) -> None:
        self.isRunning = False
        self.mainThread.join()
        #à voir pour que ça exit direct et pas que ça attende la fin de la boucle

    def is_running(self) -> bool:
        if (self.isLoopActive):
            return True
        return self._isRunning

    def update_worker(self, interface):
        timeEllapsed = -1
        while (self._isRunning):
            self._isRunning = False
            for light in self.lights:
                self._isRunning = light.set_next_event(timeEllapsed) or self._isRunning
            interface.set_frame(self.universe.serialise())
            interface.send_update()
            timeEllapsed = self.timer.get_time()
            
        if self.isLoopActive:
            self.refillMutex.acquire()
            self.timer.stop()
            self.timer = Timer()
            for light in self.lights:
                light.loop_refill()            
            self.refillMutex.release()
            timeEllapsed = -1
            self.timer.start()
            self.isRunning = True
            self._isRunning = True

    def _worker(self, interfaceName:str) -> None:
        self.isRunning = True
        self._isRunning = True
        interface = dmx.DMXInterface(interfaceName)
        self.timer.start()
        self.update_worker(interface)
        while (self.isLoopActive):
            self.update_worker(interface)
                
        self.isRunning = False
        self.timer.stop()
        interface.close()
    
    def get_time(self) -> float:
        return self.timer.get_time()
