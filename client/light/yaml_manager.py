import yaml
import os
import sys
import config
from pathlib import Path
from frame import Frame, FREQUENCY, MergeType
from typing import List

##############################################################
################         YAML READER         #################
##############################################################


class YamlReader:

    @staticmethod
    def _read_yaml(fileName:str) -> any:
        try:
            with open(fileName, 'r') as file:
                data = yaml.safe_load(file)
                return data
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise ValueError(f"Error reading YAML file: {e}")
    
    @staticmethod
    def file_to_frame(file_name:str, nbLights:int) -> Frame:
        data = YamlReader._read_yaml(file_name)
        frame = Frame(nbLights)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        for item in data:
            for tram in item["times"]:
                frame.append(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"])
        return frame
    
    @staticmethod
    def load_file(file_name, player, offset = 0, relativeOffset=False):
        data = YamlReader._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        player.add_new_set()
        for item in data:
            for tram in item["times"]:
                player.add(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"], offset, relativeOffset)


    
    
    
##############################################################
################         YAML WRITER         #################
##############################################################


class YamlWritter:
    
    @staticmethod
    def frame_to_file(fileName:str, frame:Frame) -> None:
        yamlWritter = YamlWritter(fileName)
        for lightId in range(len(frame.frames)):
            for sample in frame.frames[lightId]:
                yamlWritter.add(lightId, sample['time'], sample["rgbw"][0], sample["rgbw"][1], sample["rgbw"][2], sample["rgbw"][3], sample["Tr"])
        yamlWritter.write() 
        
    @staticmethod
    def merge_yamls(fileNames:List[str], outputFileName:str, nbLights:int, mergeType:MergeType) -> int:
        if (len(fileNames) == 0):
            return 0
        finalFrame = YamlReader.file_to_frame(fileNames[0], nbLights)
        for i in range(1, len(fileNames)):
            finalFrame = Frame.merge(finalFrame, YamlReader.file_to_frame(fileNames[i], nbLights), mergeType)
        YamlWritter.frame_to_file(outputFileName, finalFrame)
        
        return len(fileNames)   
    
    @staticmethod
    def merge_yamls_in_directory(directoryName:str, outputFileName:str, nbLights:int, mergeType:MergeType) -> int:
        filePaths = []
        for fileName in os.listdir(directoryName):
            if fileName.endswith(".yaml"):
                filePaths.append(os.path.join(directoryName, fileName))
                print("Merge directory : found file\t", filePaths[-1])
        
        return YamlWritter.merge_yamls(filePaths, outputFileName, nbLights, mergeType)
    
    
    def __init__(self,fileName:str):
        self.name = fileName
        base_path = Path(__file__).parent.parent
        folder_path = base_path 
        
        self.file_path = folder_path / f"{fileName}"
        
        if self.file_path.exists():
            print(f"The file '{fileName}' already exists.")
            if not(input("Write anyway ? (Y/N)").upper() in ["Y", "YE", "YES", "O", "OU", "OUI"]):
                sys.exit(1)
        self.fileOpened = False
        self.data = [{"id": i, "times": []} for i in range(54)]
                   


    def add(self, id:int, time:int, red:int, green:int, blue:int, white:int, Tr:int):
        
        if id < 0 or id > 53:
            print(f"The id '{id}' doesn't exists.")
            sys.exit(1)

        if time < 0:
            print(f"time can't be negative ({time}).")
            sys.exit(1)

        if not(0 <= red <= 255) or not(0 <= green <= 255) or not(0 <= blue <= 255) or not(0 <= white <= 255):
            print(f"Invalid colors ({red},{green},{blue},{white}).")
            sys.exit(1)

        if Tr != 0 and Tr != 1:
            print(f"Wrong Tr ({Tr}).")
            sys.exit(1)

             

        self.data[id]['times'].append({
            'time': int(time),
            'red': int(red),
            'green': int(green),
            'blue': int(blue),
            'white': int(white),
            'Tr': int(Tr)
        })

    
    def write(self) -> None:
        if self.fileOpened:
            yaml.dump(self.data, self.file, default_flow_style=False)
        else:
            self.isOpened = True
            with open(self.file_path , 'w') as file:
                yaml.dump(self.data, file, default_flow_style=True)
            self.isOpened = False
            
        