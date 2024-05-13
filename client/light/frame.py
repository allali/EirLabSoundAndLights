from enum import Enum
from typing import List, Tuple
from StaticLightPlayer import FREQUENCY, Player

##############################################################
###############         FRAME MANAGER         ################
##############################################################
      
class MergeType(Enum):
    MEAN=0
    MAX=1
    MIN=2

class OffsetType(Enum):
    RELATIVE=1
    ABSOLUTE=2
      
class Frame:
        
    def __init__(self, nbLights:int):
        self.frames:List[List[dict[str,any]]] = [[] for i in range(nbLights)]
        self.nbLights = nbLights
        
    @staticmethod
    def adjust_time(time:int) -> int:
        if time % FREQUENCY == 0:
            return time
        return int(time + FREQUENCY - time % FREQUENCY)
        
    def add_frame(self, lightId:int, time:int, rgbw:List[int], Tr:int) -> None:
        if (self.frames[lightId] != [] and self.frames[lightId][-1]["time"] + FREQUENCY > Frame.adjust_time(time) ):
            raise ValueError(f"Wrong frame's time given : {time} -> {Frame.adjust_time(time)}. Expected time >= {self.frames[lightId][-1]['time']+FREQUENCY} for light {lightId}")
        self.frames[lightId].append({"time": Frame.adjust_time(time), "rgbw":rgbw, "Tr": Tr})
    
    @staticmethod
    def _get_middle_frame_point(frameStart:'Frame', frameEnd:'Frame', timeMiddlePoint:int) -> dict[str,any]:
        if frameEnd is None:
            raise ValueError("FrameStop should not be None")
        if frameStart is None:
            return {"time":timeMiddlePoint, "rgbw":[0,0,0,0], "Tr":0}
        
        if timeMiddlePoint > frameEnd["time"] or timeMiddlePoint < frameStart["time"]:
            raise ValueError(f"timeMiddlePoint should be between frameStart and frameEnd times. {frameStart['time']} <= {timeMiddlePoint} <= {frameEnd['time']}")
        
        if frameEnd["Tr"] == 1:
            ratio = (timeMiddlePoint - frameStart["time"]) / (frameEnd["time"] - frameStart["time"])
            middleRgbw = [int(frameStart["rgbw"][i] + (frameEnd["rgbw"][i] - frameStart["rgbw"][i]) *ratio) for i in range(4)]
            return {"time": timeMiddlePoint, "rgbw":middleRgbw, "Tr": 1}
        
        elif frameEnd["Tr"] == 0:
            return {"time":timeMiddlePoint, "rgbw":frameStart["rgbw"], "Tr":0}
        
        raise ValueError("Unknown transition type")
        
    @staticmethod
    def _create_compatible_frames(frame1:'Frame', frame2:'Frame') -> Tuple[List[dict[str, any]],List[dict[str, any]]]:
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
                    cptFrame2.append(Frame._get_middle_frame_point(None, frame2[f2Idx], t1))
                elif f2Idx == len(frame2):
                    cptFrame2.append(Frame._get_middle_frame_point(None, frame2[f2Idx-1], t1))
                else: 
                    cptFrame2.append(Frame._get_middle_frame_point(frame2[f2Idx-1], frame2[f2Idx], t1))
                f1Idx += 1
                if f1Idx < len(frame1):
                    t1 = frame1[f1Idx]["time"]
                else:
                    t1 = frame2[-1]["time"] +1
                    
            elif t1 > t2:
                cptFrame2.append({"time":t2, "rgbw":frame2[f2Idx]["rgbw"], "Tr":frame2[f2Idx]["Tr"]})
                if f1Idx == 0:
                    cptFrame1.append(Frame._get_middle_frame_point(None, frame1[f1Idx], t2))
                elif f1Idx == len(frame1):
                    cptFrame1.append(Frame._get_middle_frame_point(None, frame1[f1Idx-1], t2))
                else:
                    cptFrame1.append(Frame._get_middle_frame_point(frame1[f1Idx-1], frame1[f1Idx], t2))
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
    
    @staticmethod
    def _color_fusion(rgbw1:List[int], rgbw2:List[int], fusionType:MergeType):
        match fusionType:
            case MergeType.MEAN: # Mean -> (c1 + c2)/2
                return [int((rgbw1[i] + rgbw2[i])/2) for i in range(4)]
            case MergeType.MAX: # Max(c1, c2)
                return [int(max(rgbw1[i], rgbw2[i])) for i in range(4)]
            case MergeType.MIN: # Min(c1, c2)
                return [int(min(rgbw1[i], rgbw2[i])) for i in range(4)]
        raise ValueError()
            
            
    @staticmethod
    def _merge(frame1:'Frame', frame2:'Frame', fusionType:MergeType) -> 'Frame':
        resultFrames = Frame(max(frame1.nbLights, frame2.nbLights))
        maxLightId = max(frame1.nbLights, frame2.nbLights)
        for lightId in range(maxLightId):
            cptFrame1, cptFrame2 = Frame._create_compatible_frames(frame1.frames[lightId], frame2.frames[lightId])
            if cptFrame1 == []:
                continue
            for idx in range(len(cptFrame1)):
                match cptFrame1[idx]['Tr'] + cptFrame2[idx]['Tr']:
                    
                    case 0:
                        resultFrames.add_frame(lightId, cptFrame1[idx]['time'], Frame._color_fusion(cptFrame1[idx]['rgbw'], cptFrame2[idx]['rgbw'], fusionType), 0)
                        
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
                            resultFrames.add_frame(lightId, newTime, Frame._color_fusion(middleRgbw, case1cptFrame2[idx-1]['rgbw'], fusionType), 1)
                        resultFrames.add_frame(lightId, case1cptFrame1[idx]['time'], Frame._color_fusion(case1cptFrame1[idx]['rgbw'], case1cptFrame2[idx]['rgbw'], fusionType), 0)
                    
                    case 2:
                        resultFrames.add_frame(lightId, cptFrame1[idx]['time'], Frame._color_fusion(cptFrame1[idx]['rgbw'], cptFrame2[idx]['rgbw'], fusionType), 1)
                    
        return resultFrames
    
    @staticmethod
    def merge(frame1:'Frame', frame2:'Frame', fusionType:MergeType) -> 'Frame':
        return Frame._merge(frame1, frame2, fusionType)
    
    
    def add_offset(self, offsetValue:int) -> 'Frame':
        res = Frame(self.nbLights)
        
        for i in range(self.nbLights):
            for frame in self.frames[i]:
                res.add_frame(i, Frame.adjust_time(frame["time"] + offsetValue), frame["rgbw"], frame["Tr"])
        return res
                                   
    
    def push(self, player:Player, mergeType:MergeType, offsetType:OffsetType, offsetValue:int) -> None:
        relativeOffset:int = offsetValue if offsetType == OffsetType.ABSOLUTE else ( int(player.get_time()) + offsetValue + 1 )
        maxSampleLen = max([len(frames) for frames in self.frames])
        
        for sampleId in range(maxSampleLen): # Adding in this order to add efficiently in the queues
            for lightId in range(self.nbLights):
                if (sampleId < len(self.frames[lightId])):
                    sample = self.frames[lightId][sampleId]
                    offsetTime:int = Frame.adjust_time(sample['time'] + relativeOffset)
                    player.add(lightId, offsetTime, sample['rgbw'], sample['Tr'], 0)
                    
                
    