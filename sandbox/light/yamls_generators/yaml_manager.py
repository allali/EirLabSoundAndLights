import sys
import yaml
from pathlib import Path

class yaml_writer:
    def __init__(self,name):
        self.name = name
        base_path = Path(__file__).parent.parent
        folder_path = base_path / 'yamls'
        folder_path.mkdir(parents=True, exist_ok=True)
        
        self.file_path = folder_path / f"{name}.yaml"
        
        if not self.file_path.exists():
            self.fileOpened = True
            # self.file = open(file_path, 'w')
            # for i in range(54):
            #     yaml.dump([{"id": i, "times": []}], self.file, default_flow_style=False)
            # self.file.close()
            self.fileOpened = False
            self.data = [{"id": i, "times": []} for i in range(54)]
            
        else:
            print(f"The file '{name}' already exists.")
            sys.exit(1)



    def add(self, id, time, red, green, blue, white, Tr):
        
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
        
        # if not file_path.exists():
        #     print(f"The file '{self.name}' doesn't exists.")
        #     sys.exit(1)
        

        self.data[id]['times'].append({
            'time': int(time),
            'red': int(red),
            'green': int(green),
            'blue': int(blue),
            'white': int(white),
            'Tr': int(Tr)
        })

    
    def write(self):
        if self.fileOpened:
            yaml.dump(self.data, self.file, default_flow_style=False)
        else:
            self.isOpened = True
            with open(self.file_path , 'w') as file:
                yaml.dump(self.data, file, default_flow_style=True)
            self.isOpened = False
        #print(self.data)
            
        

if __name__ == "__main__":
    yw = yaml_writer("test")
    yw.add(2, 100, 0, 0, 255, 200, 0)
    yw.write()
