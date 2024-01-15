from typing import List
import csv
import numpy as np
import time
import dmx
from data_file_readers import slot_transition, continuous_transition, rainbow

# Dictionnaire contenant les modules pouvant décrupter les lignes dans le csv (un module par type - type 0 ou 1 pour l'instant)
DATA_FILES_READERS = {
    "slot_transition" : slot_transition,
    "continuous_transition" : continuous_transition,
    "rainbow" : rainbow
}




# Traduit un fichier csv en un tableau ordonné compréhensible par la classe LightLauncher
class FileTranscripter:


    def __init__(self, fileName:str, nbLights:int, timeStep:int = 35):
        t0 = time.time()
        self.check_init_values(nbLights, timeStep)
        self.fileName = fileName
        self.nbLights = nbLights
        self.timeStep = timeStep
        self.lineTraducter:List[int] = []
        
        fileRawData:List[List[str]] = self.get_list_from_file()
        t1 = time.time()

        transcriptedData = []
        for lineNumber,line in enumerate(fileRawData):
            lineIdentifier = self.get_line_identifier(line, lineNumber)
            try:
                transcriptedData.extend(DATA_FILES_READERS[lineIdentifier].transcript_line(line, self.timeStep))
            except Exception as err:
                raise Exception(f"\nError at line {self.lineTraducter[lineNumber]} in csv file\n" + str(err))
        t2 = time.time()
        transcriptedData.sort()
        t3 = time.time()
 
        transcriptionSolver = TranscriptionSolver(transcriptedData, self.nbLights, self.timeStep)
        t4 = time.time()
        transcriptionSolver.solve()
        t5 = time.time()
      

        self.data = LightDataContainer(54, transcriptionSolver.get_data_set())   

        t6 = time.time() 

        tmp1 = str(round(t1 - t0,3))
        tmp2 = str(round(t2 - t1,3))
        tmp3 = str(round(t3 - t2,3))
        tmp4 = str(round(t4 - t3,3))
        tmp5 = str(round(t5 - t4,3))
        tmp6 = str(round(t6 - t5,3))
        print("\ncsv to 1st raw list : " + tmp1 + " s")
        print("transcript raw lines in raw trams : " + tmp2 + " s")
        print("sort raw trams : " + tmp3 + " s")
        print("Create transcription solver : " + tmp4 + " s")
        print("solving : " + tmp5 + " s")
        print("Creating LightDataContainer : " + tmp6 + " s\n")

    def get_data(self):
        return self.data

    
    def check_init_values(self, nbLights:int, timeStep:int):
        if (nbLights < 1 or nbLights > 512):
            raise Exception(f"FileTranscripter : given number of lights should be between 1 and 512.\nGiven value : {nbLights}")
        if (timeStep < 33):
            raise Exception(f"FileTranscripter : given time step should be greater or equal than 33.\nGiven value : {timeStep}")
        if (timeStep > 100):
            print(f"Warning :\nTime step given for FileTranscripter is high.\nGiven value : {timeStep}")
    
    def get_list_from_file(self):
        data = []
        with open(self.fileName, "r") as csvFile:
            rd = csv.reader(csvFile, delimiter=",", quotechar="|")
            for i, row in enumerate(rd):
                if (row == [] or ('#' in row[0] and row[0][0] == "#")): # Empty line or comment line
                    continue
                elif (row[0].isdigit()): # correct data line
                    data.append(row)
                    self.lineTraducter.append(i+1)
                else: # incorrect data line
                    raise Exception(f"Error in {self.fileName} at line {self.lineTraducter[i]} : incorrect line structure")
        return data

    def get_line_identifier(self, line : List, lineNumber : int):
        lineIdentifierString:str = line[0]
        if (lineIdentifierString.isdigit()):
            lineIdentifierInt = int(lineIdentifierString)
            if (0 <= lineIdentifierInt and lineIdentifierInt < len(DATA_FILES_READERS)):
                return list(DATA_FILES_READERS.keys())[lineIdentifierInt]
            else:
                raise Exception(f"FileTranscripter : Error at line {self.lineTraducter[i]}\nLine first argument is incorrect. Should be between 0 and {len(DATA_FILES_READERS)-1}.\nGiven value : {lineIdentifierInt}")
        else:
            raise Exception(f"FileTranscripter : Error at line {self.lineTraducter[i]}\nLine first argument is incorrect. It should be an integer.")
    
    
##################################################################################################################################
        

# Ajuste (modifie) les temps fournit dans le fichier csv de manière à pouvoir envoyer des trames à des fréquences régulières, sans aller trop vite
class TranscriptionSolver:

    def __init__(self, dataSet, nbLights, timeStep):
        self.dataSet:List[List[int]] = dataSet # dataSet is sorted
        self.nbLights = nbLights
        self.timeStep = timeStep
        self.timeStamps = set()
        self.cellPos = [-1] * nbLights
        self.add = 0
    
    def solve(self):
        # Normalize all the time stamps by putting at least timeStep time between them (due to DMX max frequency)
        t0 = time.time()
        for i in range(len(self.dataSet)-1):
            if (self.dataSet[i+1][1] - self.dataSet[i][1] < self.timeStep and self.dataSet[i][0] == self.dataSet[i+1][0]):
                raise Exception(f"WARNING : time stamps too close for light {self.dataSet[i][0]} with time stamp {self.dataSet[i][1]} and {self.dataSet[i+1][1]}")
            self.dataSet[i][1] -= self.dataSet[i][1] % self.timeStep # Tweaking time stamps
            self.timeStamps.add(self.dataSet[i][1]) # Adding timeStamp in timeStamp list if it is not already in it
            if (self.dataSet[i][0] != self.dataSet[i+1][0]): # If the next line in tab isn't the same light
                self.cellPos[self.dataSet[i+1][0]] = i+1 #register the beginning of light i+1 data in tab
                if (self.dataSet[i+1][1] != 0):
                    raise Exception(f"No value written at time stamp 0 for light {self.dataSet[i+1][0]}")
        self.dataSet[-1][1] -= self.dataSet[-1][1] % self.timeStep # Tweaking time stamp - border condition
        self.timeStamps.add(self.dataSet[-1][1])
        
        if (self.dataSet[0][0] == 0 and self.dataSet[0][1] == 0):
            self.cellPos[0] = 0
        
        if -1 in self.cellPos:
            raise Exception(f"No value for light {self.cellPos.index(-1)} in csv file. You must write at least the color value for time stamp 0")
        
        self.timeStamps = list(self.timeStamps)
        self.timeStamps.sort()
        t1 = time.time()
        for lightId in range(self.nbLights): 
            self.solve_unfilled_time_stamps(lightId) # some time stamps are missing for some lights
        self.dataSet.sort()
        t2 = time.time()
        print("Normalizing timeStamps : " + str(round(t1-t0,3)) + " s")
        print("Filling unwritten time stamps : " + str(round(t2-t1,3)) + " s")
          
        
    def solve_unfilled_time_stamps(self, lightId:int):
        # Ensure that for each time stamp, every light has a color set up. If not, copy paste the value of the previous time stamp
        lightStartInSet = self.cellPos[lightId] + self.add
        lightStopInSet = self.cellPos[lightId+1] + self.add if lightId != self.nbLights-1 else len(self.dataSet)
        lightTimeStamps = [arr[1] for arr in self.dataSet[lightStartInSet: lightStopInSet]]
        for timeStampId, timeStamp in enumerate(self.timeStamps):
            if (timeStampId == len(lightTimeStamps) or timeStamp != lightTimeStamps[timeStampId]):
                r,g,b,w = self.dataSet[lightStartInSet+timeStampId-1][2:6]
                toInsertInSet = [lightId, timeStamp, r, g, b, w]
                self.dataSet.insert(lightStartInSet+timeStampId, toInsertInSet)
                lightTimeStamps.insert(timeStampId, timeStamp)
                self.add += 1
                lightStopInSet += 1
    
    def get_data_set(self):
        return self.dataSet


##################################################################################################################################

# Classe contenant le tableau ordonné représentant les trames à envoyer.
class LightDataContainer:
    defaultColor:List[int] = [255, 255, 255, 200]

    def __init__(self, nbLights:int, dataSet):
        self.nbLights = nbLights

        tmpTimeStamps = list(set([arr[1] for arr in dataSet]))
        tmpTimeStamps.sort()
        self.timeStamps = np.array(tmpTimeStamps, dtype=np.uint32)
        self.lightColors = np.zeros((len(self.timeStamps), self.nbLights, 4), dtype=np.uint8)
        self.dataSize = len(self.timeStamps)
        self.lightColors = np.array(np.reshape(dataSet, (len(self.timeStamps), self.nbLights, 6), order='F')[:,:,2:], dtype=np.uint8)
        


##################################################################################################################################

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


# Récupère un tableau ordonné représentant les trames à envoyer, puis peut lancer la simulation
class LightLauncher:


    def __init__(self, lightDataContainer:LightDataContainer, interface : dmx.DMXInterface):
        self.dataFile = lightDataContainer
        self.chrono = Chronometer()
        self.interface = interface
        self.universe = dmx.DMXUniverse()
        self.dataLine = 0
        self.lights={}
        for i in range(self.dataFile.nbLights):
            l=dmx.DMXLight4Slot(address=dmx.light.light_map[i])
            line=i%6
            column=int(i/6)
            self.lights[i]={"light":l,"x":line*2,"y":column*2,"line":line,"col":column}
            self.universe.add_light(l)
    

    def start(self):
        self.chrono.start()
        for lightId, l in enumerate(self.lights.values()):
            r,g,b,w = self.dataFile.lightColors[0, lightId, :]
            l["light"].set_colour(dmx.Color(r,g,b,w))
        self.interface.set_frame(self.universe.serialise())
        self.interface.send_update()
        self.loop()
        
    def read(self):
        timeEllapsed = self.chrono.get_time()
        if self.dataFile.timeStamps[self.dataLine] < timeEllapsed:
            self.dataLine += 1
            return
        
        for lightId, l in enumerate(self.lights.values()):
            r,g,b,w = self.dataFile.lightColors[self.dataLine, lightId, :]
            l["light"].set_colour(dmx.Color(r,g,b,w))
       
        
        self.interface.set_frame(self.universe.serialise())
        self.interface.send_update()

    def reset_lights(self):
        for l in self.lights.values():
            r,g,b,w = self.dataFile.defaultColor
            l["light"].set_colour(dmx.Color(r,g,b,w))
        self.interface.set_frame(self.universe.serialise())
        self.interface.send_update()

    
    def loop(self):
        while (self.dataLine < self.dataFile.dataSize):
            self.read()
        self.reset_lights()
        self.chrono.stop()
        


if __name__ == "__main__":
    t0 = time.time()
    fileTranscripter = FileTranscripter("scenario.csv", 54)
    t1 = time.time()
    lightData = fileTranscripter.get_data()
    del fileTranscripter
    t2 = time.time()
    launcher = LightLauncher(lightData, dmx.DMXInterface("TkinterDisplayer"))
    t3 = time.time()
    tmp1 = str(round(t1 - t0,3))
    tmp2 = str(round(t2 - t1,3))
    tmp3 = str(round(t3 - t2,3))
    tmp4 = str(round(t3 - t0,3))
    
    print("FileTranscripter : " + tmp1 + " s")
    print("del : " + tmp2 + " s")
    print("LightLauncher : " + tmp3 + " s")
    print("\nTotal : " + tmp4 + " s")
    launcher.start()