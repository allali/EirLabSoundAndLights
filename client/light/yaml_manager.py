import yaml
import sys
from pathlib import Path
from frame import Frame

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
                frame.add_frame(item["id"], tram["time"], [tram['red'], tram['green'], tram['blue'], tram['white']], tram["Tr"])
        return frame
    
    
    
    
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
    
    def __init__(self,fileName:str):
        self.name = fileName
        base_path = Path(__file__).parent.parent
        folder_path = base_path 
        folder_path.mkdir(parents=True, exist_ok=True)
        
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

        base_path = Path(__file__).parent
        folder_path = base_path / 'yamls'
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / f"{self.name}.yaml"
             

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
            
        