import csv
import numpy as np
from typing import List
import time
import dmx

class DataFile:

    def getIds(self, rowTxt : str):
        if ';' in rowTxt:
            FragmentedRowTxt = rowTxt.split(";")
            lightIds = [self.getIds(RowTxtFragment) for RowTxtFragment in FragmentedRowTxt]
            return lightIds
        
        elif ":" in rowTxt:
            start, stop = map(int, rowTxt.split(":"))
            if (start < 0 or stop >= self.nbLights):
                raise ValueError(f"Lights ids are not in the range [{0}:{self.nbLights}[")
            lightIds = [k for k in range(start, stop+1)]
            return lightIds
        
        elif rowTxt.isdigit() and int(rowTxt) >= 0 and int(rowTxt) < self.nbLights:
            return [int(rowTxt)]
        
        raise ValueError("Wrong light id")
    
    def check_light_values(self, lightValues : List[int]):
        for i in range(4):
            if not(lightValues[i].isdigit()):
                raise ValueError("Lights color values (RGBW) must be digits")
            lightValueDigit = int(lightValues[i])
            if lightValueDigit < 0 or lightValueDigit > 255:
                raise ValueError("Lights color values (RGBW) must be between 0 and 255")


    def __init__(self, fileName : str, nbLights : int):
        rowData = read_file(fileName)
        timeStamps = [row[0] for row in rowData if row[0].isdigit()]
        self.dataSize = len(set(timeStamps)) + rowData.count(["default"]) +1
        self.nbLights = nbLights
        self.lightData = np.zeros((self.dataSize, nbLights, 4), dtype = np.uint8) 
        self.timeData = np.zeros((self.dataSize), dtype = np.uint32)
        self.switchType = np.zeros((self.dataSize), dtype=np.uint8)
        self.lightData[:, :, :3] = 180
        self.lightData[:, :, 3] = 255
        self.timeData[:] = 0
        self.switchType[:] = 1

        lastTime = -1
        shift = 0
        for i, row in enumerate(rowData):
            if len(row) == 1 and row[0] == "default":
                self.timeData[i-shift] = 0 if i-shift ==0 else self.timeData[i-shift-1]+2000
                self.lightData[i-shift, :, :3] = 255
                self.lightData[i-shift, :, 3] = 200
                self.switchType[i-shift] = 1
                self.lightData[i-shift+1, :, :] = self.lightData[i-shift, :, :]

            elif len(row) == 7:
                if (int(row[0]) == lastTime):
                    shift+=1
                elif (int(row[0]) < lastTime):
                    raise Exception(f"Time indices in csv file must crescent. Error at line {i+2} in csv file")
                self.timeData[i-shift] = int(row[0])
                lastTime = self.timeData[i-shift]
                self.switchType[i-shift] = int(row[6])
                lightIds = self.getIds(row[1])
                self.check_light_values(row[2:6])
                for lightId in lightIds:
                    self.lightData[i-shift, lightId, :] = np.array(list(map(int, row[2:6])))
                self.lightData[i-shift+1, :, :] = self.lightData[i-shift, :, :]
            
            else:
                raise Exception(f"Unknown structure at line {i+2} in csv file {fileName}")

        self.switchType[0] = 0
            



        



def read_file(fileName : str):
    result = []
    with open(fileName, "r") as csvFile:
        rd = csv.reader(csvFile, delimiter=",", quotechar="|")
        for i, row in enumerate(rd):
            if i == 0:
                print("file description :", "".join(row))
            elif row != []:
                result.append(row)
    return result

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



class DataReader:

    def __init__(self, dataFile : DataFile, interface : dmx.DMXInterface):
        self.dataFile = dataFile
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
        if self.dataFile.timeData[0] == 0:
            for lightId, l in enumerate(self.lights.values()):
                r,g,b,w = self.dataFile.lightData[0, lightId, :]
                l["light"].set_colour(dmx.Color(r,g,b,w))
            self.interface.set_frame(self.universe.serialise())
            self.interface.send_update()
        self.loop()
        
    def read(self):
        timeEllapsed = self.chrono.get_time()
        if self.dataFile.timeData[self.dataLine] < timeEllapsed:
            self.dataLine += 1
            return
        if self.dataFile.switchType[self.dataLine] == 0:
            for lightId, l in enumerate(self.lights.values()):
                r,g,b,w = self.dataFile.lightData[self.dataLine, lightId, :]
                l["light"].set_colour(dmx.Color(r,g,b,w))
        elif self.dataFile.switchType[self.dataLine] == 1:
            start = self.dataFile.timeData[self.dataLine-1]
            stop = self.dataFile.timeData[self.dataLine]
            for lightId, l in enumerate(self.lights.values()):
                ratio = (stop -timeEllapsed) / (stop - start)
                r,g,b,w = np.average([self.dataFile.lightData[self.dataLine-1, lightId, :], self.dataFile.lightData[self.dataLine, lightId, :]], axis=0, weights=[ratio, 1-ratio])
                l["light"].set_colour(dmx.Color(r,g,b,w))
        
        self.interface.set_frame(self.universe.serialise())
        self.interface.send_update()
    
    def loop(self):
        while (self.dataLine < self.dataFile.dataSize):
            self.read()
        self.chrono.stop()
        





d = DataFile("desc.csv", 54)
dr = DataReader(d, dmx.DMXInterface("TkinterDisplayer"))
dr.start()