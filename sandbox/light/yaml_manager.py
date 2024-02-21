import sys
import yaml
from pathlib import Path

def create_yaml(name):
    base_path = Path(__file__).parent
    folder_path = base_path / 'yamls'
    folder_path.mkdir(parents=True, exist_ok=True)
    
    file_path = folder_path / f"{name}.yaml"
    
    if not file_path.exists():
        with open(file_path, 'w') as file:
            for i in range(54):
                yaml.dump([{"id": i, "times": []}], file, default_flow_style=False)
    else:
        print(f"The file '{name}' already exists.")
        sys.exit(1)


def add_to_yaml(name, id, time, red, green, blue, white, Tr):

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
    
    file_path = folder_path / f"{name}.yaml"
    
    if not file_path.exists():
        print(f"The file '{name}' doesn't exists.")
        sys.exit(1)
    
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    data[id]['times'].append({
        'time': time,
        'red': red,
        'green': green,
        'blue': blue,
        'white': white,
        'Tr': Tr
    })

    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


create_yaml("test")
add_to_yaml("test", 2, 100, 0, 0, 255, 200, 0)