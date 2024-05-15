from typing import List
from enum import Enum

import threading
from collections import deque
import time

from light import dmx, lightConfig
FREQUENCY:int = 27


class OffsetType(Enum):
    RELATIVE=1
    ABSOLUTE=2

        
##############################################################
###################         TIMER         ####################
##############################################################

class Timer:
    def __init__(self):
        self.startTime = None

    def start(self) -> None:
        """Starts the timer at t=0"""
        self.startTime = time.time()

    def stop(self) -> float:
        """Stops the timer"""
        timeEllapsed = self.get_time()
        self.startTime = None
        return timeEllapsed
        
    def get_time(self) -> float:
        """Returns the time ellapsed from start in milliseconds"""
        if self.startTime is not None:
            timeEllapsed = (time.time() - self.startTime) * 1000
            return timeEllapsed
        else:
            return 0
            raise ValueError("Timer has not been started")
        
        
        
##############################################################
############         SINGLE LIGHT PLAYER         #############
##############################################################
        

# Light player for one light
class SingleLightQueue:
    def __init__(self, lightId:int, queueMaxSize:int | None, isLoopActive : bool):
        self.lightId:int = lightId
        self.queue = deque([], queueMaxSize)
        self.history = deque([], None)
        self.light = dmx.DMXLight4Slot(address=lightConfig.light_map[lightId])
        self.isRunning:bool = True
        self.current_event = None
        self.next_event = None
        self.transition_step_size = 0
        self.transition_progress = 0
        self.lastUpdateTime = 0
        self.LastTransition_rgbw = [0,0,0,0]
        self.mutex = threading.Lock()
        self.isLoopActive = isLoopActive
        

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
        print(f"Add failed for light n°{self.lightId}. Expected timestamp higher than {self.queue[-1][0]} (last timestamp in queue), but got {time}")
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
        if self.isLoopActive:
            self.history.append(elmt)
    
    def is_running(self) -> bool:
        return len(self.queue) != 0
             
        

        
##############################################################
###############         LIGHT PLAYER         #################
##############################################################


# Static light player manager all your lights
class StaticLightsPlayer:
    """A Light Player for rgbw lights to control with DMX.
    """
    
    def __init__(self, nbLights:int, interfaceName:str, isLoopActive:bool=False):
        """Creates a Static Light Player.

        Parameters
        ----------
        nbLights : int
            The number of lights to control.
        interfaceName : int
            The name of the interface to use (either "TkinterDisplayer", "FT232R" or "Dummy").
        isLoopActive : bool
            If set to True, the queue will resume from the start when there will be no more orders to read in the queues
        """
        self.timer:Timer = Timer()
        self.universe:dmx.DMXUniverse = dmx.DMXUniverse()
        self.interface_name:str = interfaceName
        self.timeEllapsed = 0

        self.nbLights:int = nbLights
        self.lights:List[SingleLightQueue] = [SingleLightQueue(i, None, isLoopActive) for i in range(nbLights)]
        self._add_lights_to_universe()

        self.mainThread:threading.Thread = threading.Thread(target=self._worker, args=[interfaceName])
        self.isRunning:bool = False     # Used by the user to close the player
        self.isLoopActive:bool = isLoopActive    # When no more orders to read in the queue, resume from start
        self.refillMutex:threading.Lock = threading.Lock()

    def _add_lights_to_universe(self) -> None:
        for light in self.lights:
            light.add_to_universe(self.universe)
       
    
    def add(self, lightId:int, time:int, rgbw:List[int], Tr:int, offsetType: OffsetType) -> None:
        """Adds an order to the queue of a light.

        Parameters
        ----------
        lightId : int
            The id of the light to which the order is related.
        time : int
            The timestamp at which the order is to be execute.
        rgbw : List[int]
            The rgbw values of your order.
        Tr : int
            The type of transition to use.
        offsetType : OffsetType
            If set to RELATIVE, adds player's current time to the time given.
        offset : int
            An offset to add to the time.

        The call to this function will be ignored if the given timestamp is smaller than the current time.

        """
        # Using timeEllapsed and not self.get_time() to avoid to many calls to time.time()
        # Adding also FREQUENCY to avoid any time conflicts
        newTime = (time + self.timeEllapsed + FREQUENCY) if offsetType == OffsetType.RELATIVE else time  
        self.refillMutex.acquire()      # This mutex is used to avoid any conflicts between 'add' and the 'loop' option
        self.lights[lightId].add(newTime, rgbw, Tr)
        self.refillMutex.release()
        
    def start(self) -> None:
        """Start the Light Player."""
        
        self.isRunning = True
        self.mainThread.start()
    
    def quit(self) -> None:
        """Closes the Player."""
        
        self.isRunning = False
        self.mainThread.join()


    def is_running(self) -> bool:
        """Returns True if the player has still orders to read.
        Always returns True is the looper is active.
        """
        if (self.isLoopActive):
            return True
        for light in self.lights:
            if light.is_running():
                return True
        return False

    def _update_worker(self, interface:dmx.DMXInterface):
        _isRunning = True
        self.timeEllapsed = 0
        while (_isRunning and self.isRunning):
            _isRunning = False
            for light in self.lights:
                _isRunning = light.set_next_event(self.timeEllapsed) or _isRunning
            interface.set_frame(self.universe.serialise())
            interface.send_update()
            self.timeEllapsed = self.timer.get_time()
            
        if self.isLoopActive:
            self.refillMutex.acquire()
            self.timer.stop()
            self.timer = Timer()
            for light in self.lights:
                light.loop_refill()            
            self.refillMutex.release()
            self.timeEllapsed = 0
            self.timer.start()
            self.isRunning = True

    def _worker(self, interfaceName:str) -> None:
        # The interface must be declared in this thread as Tkinter does not allow multi-thread access to its windows
        # We can't also declared 'interface' as an instance variable as tkinter consider it like allowing its access to other threads
        interface = dmx.DMXInterface(interfaceName)
        self.timer.start()
        self._update_worker(interface)
        while (self.isLoopActive):  # for the 'loop' option
            self._update_worker(interface)
                
        self.isRunning = False
        self.timer.stop()
        interface.close()
    
    def get_time(self) -> float:
        """Returns the current relative time of the Player in milliseconds."""
        return self.timer.get_time()
