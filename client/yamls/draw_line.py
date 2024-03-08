import yaml
import numpy as np
from yaml_manager import yaml_writer
from tqdm import tqdm


def format_print(values):
    for line in range(53, 47, -1):
        for idxValue in [line-6*i for i in range(9)]:
            print(str(values[idxValue])[:5], end="  ")
        print()
        



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
    lights_data = data[0]["lights"]
    speakers_data = data[1]["speakers"]
    
    for lightId, light in enumerate(lights_data):
        if lightId != light["id"]:
            ValueError(f"Exepected id {lightId}, got { light['id'] }")
        lights.append([light["x"], light["y"], light["z"]])
        
    for speakerId, speaker in enumerate(speakers_data):
        if speakerId != speaker["id"]:
            ValueError(f"Exepected id {speakerId}, got { speaker['id'] }")
        speakers.append([speaker["x"], speaker["y"], speaker["z"]])
    
    return (np.array(lights), np.array(speakers))
        
    

lights, speakers = load_file(r"../config/3D_coordinates_device.yml")



def dist(P1, P2):
    return np.sum((P2-P1)**2)
    #return ( (P2[0]-P1[0])**2 ) + ( (P2[1]-P1[0])**2 ) + ( (P2[2]-P1[2])**2 )


def get_line_step(Pi, Pf, ratio:float):
    if (ratio > 1 or ratio < 0):
        raise ValueError(f"Expected ratio between 0 and 1, got f{ratio}")
    if len(Pi) != len(Pf):
        raise ValueError("initial and final dimensions are different")
    currentPos = Pi + (Pf-Pi)*ratio 
    distanceTable = np.zeros((len(lights)), dtype=np.float64)
    for lightId, light in enumerate(lights):
        distanceTable[lightId] = dist(currentPos, light)
    distanceTable = np.sqrt(distanceTable)
    return distanceTable

def normalize_data_set(dataSet):
    """
    Normalize values from dataSet between 0 and 1
    """
    dataSet -= np.min(dataSet)
    return dataSet/np.max(dataSet)

def distance_map_to_rgbw(dataSet):
    colorMap = np.zeros((dataSet.size, 4), dtype=np.uint8)
    colorMap[:, 0] = dataSet*255
    colorMap[:, 1] = dataSet*255
    colorMap[:, 2] = dataSet*255
    colorMap[:, 3] = dataSet*255
    return colorMap
    
    
def get_color_anim(ym ,startPosition, endPosition, offset:int, duration:int, func=lambda x:(x**5)):
    for i in range(min(10, int(duration//27 - 1))):
        dataSet = get_line_step(startPosition, endPosition, i/(duration//27))
        dataSet = 1 - normalize_data_set(dataSet)
        dataSet = func(dataSet)
        colorMap = distance_map_to_rgbw(dataSet)
        for lightId, color in enumerate(colorMap):
            ym.add(lightId, offset+ i*27, color[0], color[1], color[2], color[3], 1)
    
    dataSet = get_line_step(startPosition, endPosition, 1)
    dataSet = 1 - normalize_data_set(dataSet)
    dataSet = func(dataSet)
    colorMap = distance_map_to_rgbw(dataSet)
    for lightId, color in enumerate(colorMap):
        ym.add(lightId, offset+ duration, color[0], color[1], color[2], color[3], 1)
        
def add_buffer(ym):
    for lightId in range(54):
        ym.add("line", lightId, 0, 0, 0, 0, 0, 0)

def static_glow(ym , position, offset:int, duration:int, func=lambda x:(x**5)):
    dataSet = np.zeros((len(lights)), dtype=np.float64)
    for lightId, light in enumerate(lights):
        dataSet[lightId] = dist(position, light)
    dataSet = np.sqrt(dataSet)
    
    dataSet = 1 - normalize_data_set(dataSet)
    dataSet = func(dataSet)
    colorMap = distance_map_to_rgbw(dataSet)
    for lightId, color in enumerate(colorMap):
        ym.add(lightId, offset, color[0], color[1], color[2], color[3], 0)
        ym.add(lightId, offset+duration, color[0], color[1], color[2], color[3], 0)

if __name__ == "__main__":
    timeline = [(0,900),
                (1250, 2250),
                (2980, 3850), 
                (4500, 5750), 
                (6250, 7400),
                (8000, 9250),
                (9820, 11000),
                (11890, 13140),
                (13970, 15270),
                (16210, 17400)]
    
    
    ym = yaml_writer("line")
    for speakerId in tqdm(range(len(speakers)-1)):
        static_glow(ym , speakers[speakerId], timeline[speakerId][0], timeline[speakerId][1] - timeline[speakerId][0])
        get_color_anim(ym, speakers[speakerId], speakers[speakerId+1], timeline[speakerId][1], timeline[speakerId+1][0] - timeline[speakerId][1])
    static_glow(ym , speakers[-1], timeline[-1][0], timeline[-1][1] - timeline[-1][0])
    ym.write()
