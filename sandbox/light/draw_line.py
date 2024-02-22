import yaml



def read_yaml(file_name):
    try:
        with open(file_name, 'r') as file:
            
            data = yaml.safe_load(file)
            return data
    except (yaml.YAMLError, FileNotFoundError) as e:
        raise ValueError(f"Error reading YAML file: {e}")
        
def load_file(file_name):
    data = read_yaml(file_name)

    if not isinstance(data, list):
        raise ValueError("Invalid YAML format. Expected a list.")
    
    lights = []
    speakers = []
    for lightId, light in enumerate(data):
        print(light["lights"])
        break
        
    
    
    print()
    
    
    
    
    
    
    
    
    print(data)

data = load_file(r"./yamls/3D_coordinates_device.yml")
