import threading
from typing import List
import yaml
import queue
import time
import sys
sys.path.append("..")
import dmx
import numpy as np
from copy import deepcopy
FREQUENCY = 27


        
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
            return 0
            raise ValueError("Timer has not been started")
        
#############################################################
        
class SingleLightQueue:
    def __init__(self, lightId:int, queueMaxSize:int):
        self.lightId:id = lightId
        self.queue = queue.Queue(maxsize=queueMaxSize)
        self.light = dmx.DMXLight4Slot(address=dmx.light.light_map[lightId])
        self.isRunning:bool = True
        self.no_event = np.array([0,0,0,0])
        self.current_event = None
        self.next_event = None
        self.transition_step_size = 0
        self.transition_progress = 0
        self.lastUpdateTime = 0
        self.LastTransition_rgbw = [0,0,0,0]

    def add_to_universe(self, dmxUniverse:dmx.DMXUniverse):
        dmxUniverse.add_light(self.light)

    
    def get_next_event(self):
        if not self.queue.empty():
            return self.queue.queue[0]
        return None

    def fill_queue(self, time:int, rgbw:List[int], Tr:int):
        self.add(time, rgbw, Tr)

    def add(self, time:int, rgbw:List[int], Tr:int):
        self.queue.put((time, rgbw, Tr))
    
    def get_queue(self):
        queueList = deepcopy(self.queue.queue) 
        if len(queueList) > 0 and queueList[0][2] == 1:
            _ = [(self.lastUpdateTime, self.LastTransition_rgbw, 0)]
            _.extend(queueList)
            return _
        return queueList
    
    def replace_queue(self, queue:queue.Queue, time:int):
        self.queue = queue
        
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
        #print(self.queue.qsize())
        self.lastUpdateTime = timeEllapsed
        if self.queue.empty():
            self.isRunning = False
            return 
        else:
            self.isRunning = True
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
                # if self.current_event[2] == 1:
                #     self.add(self.current_event[0], self.current_event[1], 0)
                # else:
                previous_time, previous_rgbw, _ = self.current_event
                total_steps = (event_time - previous_time) // FREQUENCY
    
                if self.transition_progress >= total_steps:
                    return
                self.transition_progress = abs((timeEllapsed - previous_time) / FREQUENCY)

                step_size = [(current - previous) / total_steps for current, previous in zip(event_rgbw, previous_rgbw)]
                self.LastTransition_rgbw = [int(previous + (step * self.transition_progress)) for previous, step in zip(previous_rgbw, step_size)]
                self.set_color(self.LastTransition_rgbw)

        if self.next_event is not None and timeEllapsed > self.next_event[0]:
            self.set_color(self.next_event[1])
            self.next_event = self.get_next_event()
            self.remove_event()

            
    def remove_event(self):
        self.queue.get()
             
        

        
#################################################

class Player:
    def __init__(self, nbLights:int, interfaceName:str):
        self.added_file_names:List[str] = []
        self.timer:Timer = Timer()
        self.time_debug:Timer = Timer()
        self.universe:dmx.DMXUniverse = dmx.DMXUniverse()
        self.interface_name:str = interfaceName

        self.nbLights:int = nbLights
        self.lights:List[SingleLightQueue] = [SingleLightQueue(i, 0) for i in range(nbLights)]
        self._add_lights_to_universe()

        self.mainThread = threading.Thread(target=self._worker, args=[interfaceName])
        self.isRunning:bool = False

    def _add_lights_to_universe(self):
        for light in self.lights:
            light.add_to_universe(self.universe)
            
    def adjust_time(self, time:int):
        return time + FREQUENCY - time % FREQUENCY

    def add(self, lightId:int, time:int, rgbw:List[int], Tr:int, offset:int):
        time = self.adjust_time( time + offset )
        self.lights[lightId].fill_queue(time, rgbw, Tr)
        
    def get_queue(self):
        return [light.get_queue() for light in self.lights]
    
    def replace_queue(self, queues):
        for lightId, light in enumerate(self.lights):
            light.replace_queue(queues[lightId], self.timer.get_time())

    def start(self):
        self.isRunning = True
        self.mainThread.start()
    
    def quit(self):
        self.isRunning = False
        self.mainThread.join()
        #à voir pour que ça exit direct et pas que ça attende la fin de la boucle

    def is_running(self):
        if not(self.isRunning):
            return False 
        for light in self.lights:
            if light.isRunning:
                return True
        return False

    def _worker(self, interfaceName:str):
        self.isRunning = True
        timeEllapsed = -1
        interface = dmx.DMXInterface(interfaceName)
        self.timer.start()
        print("starting")
        while (self.isRunning):
            for light in self.lights:
                light.set_next_event(timeEllapsed)
            interface.set_frame(self.universe.serialise())
            interface.send_update()
            self.isRunning = self.is_running()
            timeEllapsed = self.timer.get_time()

        self.timer.stop()
        interface.close()
    
    def get_time(self):
        return self.timer.get_time()

##################################################


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
    
    def load_file(self, file_name:str, player:Player, offset:int = 0):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        player.added_file_names.append(file_name)
        for item in data:
            for tram in item["times"]:
                player.add(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"], offset)
    
    def get_frame(self, file_name:str, nbLights:int):
        data = self._read_yaml(file_name)
        frame = Frame(nbLights)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        player.added_file_names.append(file_name)
        for item in data:
            for tram in item["times"]:
                frame.add_frame(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"])
        return frame
     
##################################################

                
class Frame:
    
    nbLights = 54
    
    def __init__(self, nbLights:int):
        self.frames:List[List[dict[str,any]]] = [[] for i in range(nbLights)]
        self.nbLights = nbLights
        
    def adjust_time(time:int):
        if time % FREQUENCY == 0:
            return time
        return int(time + FREQUENCY - time % FREQUENCY)
        
    def add_frame(self, lightId:int, time:int, rgbw:List[int], Tr:int):
        if (self.frames[lightId] != [] and self.frames[lightId][-1]["time"] + FREQUENCY > Frame.adjust_time(time) ):
            raise ValueError(f"Wrong frame's time given : {time} -> {Frame.adjust_time(time)}. Expected time >= {self.frames[lightId][-1]['time']+FREQUENCY} for light {lightId}")
        self.frames[lightId].append({"time": Frame.adjust_time(time), "rgbw":rgbw, "Tr": Tr})
    
    def get_middle_frame_point(self, frameStart, frameEnd, timeMiddlePoint):
        if frameEnd is None:
            raise ValueError("FrameStop should not be None")
        if frameStart is None:
            return {"time":timeMiddlePoint, "rgbw":frameEnd["rgbw"], "Tr":0}
        
        if timeMiddlePoint > frameEnd["time"] or timeMiddlePoint < frameStart["time"]:
            raise ValueError(f"timeMiddlePoint should be between frameStart and frameEnd times. {frameStart['time']} <= {timeMiddlePoint} <= {frameEnd['time']}")
        
        if frameEnd["Tr"] == 1:
            ratio = (timeMiddlePoint - frameStart["time"]) / (frameEnd["time"] - frameStart["time"])
            middleRgbw = [int(frameStart["rgbw"][i] + (frameEnd["rgbw"][i] - frameStart["rgbw"][i]) *ratio) for i in range(4)]
            return {"time": timeMiddlePoint, "rgbw":middleRgbw, "Tr": 1}
        
        elif frameEnd["Tr"] == 0:
            return {"time":timeMiddlePoint, "rgbw":frameStart["rgbw"], "Tr":0}
        
        raise ValueError("Unknown transition type")
        
        
    def create_compatible_frames(self, frame1, frame2):
        cptFrame1 = []
        cptFrame2 = []
        f1Idx = 0
        f2Idx = 0
            
        if len(frame1) ==0:
            return frame2, frame2
        if len(frame2) == 0:
            return frame1, frame1
        
        if frame1[0]["Tr"] == 1 or frame2[0]["Tr"] == 1:
            raise ValueError("Cannot begin with Tr 1")
        
        if frame1[0]["time"] < frame2[0]["time"]:
            cptFrame1.append(frame1[0])
            cptFrame2.append({"time":frame1[0]["time"], "rgbw":frame2[0]["rgbw"], "Tr":frame2[0]["Tr"]})
            t1 = frame1[1]["time"] if len(frame1) > 1 else frame2[-1]["time"] +1
            t2 = frame2[0]["time"]
            f1Idx = 1
            f2Idx = 0
        elif frame1[0]["time"] > frame2[0]["time"]:
            cptFrame1.append({"time":frame2[0]["time"], "rgbw":frame1[0]["rgbw"], "Tr":frame1[0]["Tr"]})
            cptFrame2.append(frame2[0])
            t1 = frame1[0]["time"]
            t2 = frame2[1]["time"] if len(frame2) > 1 else frame1[-1]["time"] +1
            f1Idx = 0
            f2Idx = 1
        else:
            cptFrame1.append({"time":frame2[0]["time"], "rgbw":frame1[0]["rgbw"], "Tr":frame1[0]["Tr"]})
            cptFrame2.append({"time":frame1[0]["time"], "rgbw":frame2[0]["rgbw"], "Tr":frame2[0]["Tr"]})
            t1 = frame1[1]["time"] if len(frame1) > 1 else frame2[-1]["time"] +1
            t2 = frame2[1]["time"] if len(frame2) > 1 else frame1[-1]["time"] +1
            f1Idx = 1
            f2Idx = 1
        
        while (f1Idx < len(frame1) or f2Idx < len(frame2)):
            if t1 < t2:
                cptFrame1.append({"time":t1, "rgbw":frame1[f1Idx]["rgbw"], "Tr":frame1[f1Idx]["Tr"]})
                if f2Idx == 0:
                    cptFrame2.append(self.get_middle_frame_point(None, frame2[f2Idx], t1))
                elif f2Idx == len(frame2):
                    cptFrame2.append(self.get_middle_frame_point(None, frame2[f2Idx-1], t1))
                else: 
                    cptFrame2.append(self.get_middle_frame_point(frame2[f2Idx-1], frame2[f2Idx], t1))
                f1Idx += 1
                if f1Idx < len(frame1):
                    t1 = frame1[f1Idx]["time"]
                else:
                    t1 = frame2[-1]["time"] +1
                    
            elif t1 > t2:
                cptFrame2.append({"time":t2, "rgbw":frame2[f2Idx]["rgbw"], "Tr":frame2[f2Idx]["Tr"]})
                if f1Idx == 0:
                    cptFrame1.append(self.get_middle_frame_point(None, frame1[f1Idx], t2))
                elif f1Idx == len(frame1):
                    cptFrame1.append(self.get_middle_frame_point(None, frame1[f1Idx-1], t2))
                else:
                    cptFrame1.append(self.get_middle_frame_point(frame1[f1Idx-1], frame1[f1Idx], t2))
                f2Idx += 1
                if f2Idx < len(frame2):
                    t2 = frame2[f2Idx]["time"]
                else:
                    t2 = frame1[-1]["time"] +1
                    
            else:
                cptFrame1.append({"time":t1, "rgbw":frame1[f1Idx]["rgbw"], "Tr":frame1[f1Idx]["Tr"]})
                cptFrame2.append({"time":t2, "rgbw":frame2[f2Idx]["rgbw"], "Tr":frame2[f2Idx]["Tr"]})
                f1Idx += 1
                f2Idx += 1
                if f1Idx < len(frame1):
                    t1 = frame1[f1Idx]["time"]
                else:
                    t1 = frame2[-1]["time"] + 1
                    
                if f2Idx < len(frame2):
                    t2 = frame2[f2Idx]["time"]
                else:
                    t2 = frame1[-1]["time"] + 1
                    
        return cptFrame1, cptFrame2
    
    def _color_fusion(self, rgbw1:List[int], rgbw2:List[int], fusionType:int):
        match fusionType:
            case 0: # Mean -> (c1 + c2)/2
                return [int((rgbw1[i] + rgbw2[i])/2) for i in range(4)]
            case 1: # Max(c1, c2)
                return [int(max(rgbw1[i], rgbw2[i])) for i in range(4)]
            case 2: # Min(c1, c2)
                return [int(min(rgbw1[i], rgbw2[i])) for i in range(4)]
            
            
    def _merge(self, frames2, fusionType:int):
        resultFrames = Frame(max(self.nbLights, frames2.nbLights))
        maxLightId = max(self.nbLights, frames2.nbLights)
        for lightId in range(maxLightId):
            cptFrame1, cptFrame2 = self.create_compatible_frames(self.frames[lightId], frames2.frames[lightId])
            if cptFrame1 == []:
                continue
            for idx in range(len(cptFrame1)):
                match cptFrame1[idx]['Tr'] + cptFrame2[idx]['Tr']:
                    
                    case 0:
                        resultFrames.add_frame(lightId, cptFrame1[idx]['time'], self._color_fusion(cptFrame1[idx]['rgbw'], cptFrame2[idx]['rgbw'], fusionType), 0)
                        
                    case 1:
                        if cptFrame1[idx]['Tr'] == 1:
                            case1cptFrame1 = cptFrame1 # Tr == 1
                            case1cptFrame2 = cptFrame2 # Tr == 0
                        else:
                            case1cptFrame1 = cptFrame2 # Tr == 1
                            case1cptFrame2 = cptFrame1 # Tr == 0
                    
                        newTime = case1cptFrame1[idx]['time'] - FREQUENCY
                        if case1cptFrame1[idx-1]['time'] < newTime and newTime >= 0: 
                            ratio = (newTime - case1cptFrame1[idx-1]["time"]) / (case1cptFrame1[idx]["time"] - case1cptFrame1[idx-1]["time"])
                            middleRgbw = [int(case1cptFrame1[idx-1]["rgbw"][i] + (case1cptFrame1[idx]["rgbw"][i] - case1cptFrame1[idx-1]["rgbw"][i]) *ratio) for i in range(4)]
                            resultFrames.add_frame(lightId, newTime, self._color_fusion(middleRgbw, case1cptFrame2[idx-1]['rgbw'], fusionType), 1)
                        resultFrames.add_frame(lightId, case1cptFrame1[idx]['time'], self._color_fusion(case1cptFrame1[idx]['rgbw'], case1cptFrame2[idx]['rgbw'], fusionType), 0)
                    
                    case 2:
                        resultFrames.add_frame(lightId, cptFrame1[idx]['time'], self._color_fusion(cptFrame1[idx]['rgbw'], cptFrame2[idx]['rgbw'], fusionType), 1)
                    
        return resultFrames
    
    def merge(frames1, frames2, fusionType:int):
        return frames1._merge(frames2, fusionType)
    
    def add_offset(self, offsetValue:int):
        res = Frame(nbLights)
        
        for i in range(self.nbLights):
            for frame in self.frames[i]:
                res.add_frame(i, Frame.adjust_time(frame["time"] + offsetValue), frame["rgbw"], frame["Tr"])
        return res
    
    def player_replace_queue(player:Player, frames, mergeType, isRelativeOffset:bool = False, relativeOffset=0):
        playerFrame = Frame(player.nbLights)
        playerQueues = player.get_queue()
        currTime = player.get_time()
        for lightId in range(player.nbLights):
            for i in range(len(playerQueues[lightId])):
                playerFrame.add_frame(lightId, playerQueues[lightId][i][0], playerQueues[lightId][i][1], playerQueues[lightId][i][2])
        
        offset = (player.get_time() if isRelativeOffset else 0) + relativeOffset
        newFrames = Frame.merge(playerFrame, frames.add_offset(offset), mergeType)
                
        queues = [queue.Queue(maxsize=0) for i in range(nbLights)]
                
        for lightId, frameQueue in enumerate(queues):
            t=-1
            for i in range(len(newFrames.frames[lightId])):
                if newFrames.frames[lightId][i]["time"] <= t:
                    raise ValueError(f"{t} and {newFrames.frames[lightId][i]['time']}, light {lightId}")
                t = newFrames.frames[lightId][i]["time"]
                frameQueue.put([newFrames.frames[lightId][i]["time"], newFrames.frames[lightId][i]["rgbw"], newFrames.frames[lightId][i]["Tr"]])
        player.replace_queue(queues)
                                
                    
                
    
    
                
   
##################################################


if __name__ == "__main__":
    
    f1 = Frame(54)
    f2 = Frame(54)
    f1.add_frame(1, 12, [1,10,100,0], 0)
    f1.add_frame(1, 50, [2,11,101,0], 1)
    f1.add_frame(1, 120, [3,12,102,0], 0)
    f1.add_frame(1, 150, [4,13,103,0], 0)
    f1.add_frame(1, 190, [5,14,104,0], 1)
    f1.add_frame(1, 250, [6,15,105,0], 0)
    
    f2.add_frame(1, 30, [10,100,200,0], 0)
    f2.add_frame(1, 101, [20,110,201,0], 1)
    f2.add_frame(1, 220, [30,120,202,0], 0)
    f2.add_frame(1, 290, [40,130,203,0], 0)
    f2.add_frame(1, 350, [50,140,204,0], 1)
    f2.add_frame(1, 4000, [60,150,205,255], 1)
    

    b= Frame.merge(f1, f2, 0)

    

    
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R",TkinterDisplayer,Dummy
    player = Player(54, interfaceName)
    yr = YamlReader()
    yamlFrame = yr.get_frame(r"../yamls/snake2.yml", 54)
    mergedFrame1 = Frame.merge(b, yamlFrame, 0)
    Frame.player_replace_queue(player, mergedFrame1,0)
    
    player.start()
    while (player.is_running()):
        time.sleep(1.6)
        Frame.player_replace_queue(player, mergedFrame1, 1, True)
    player.quit()