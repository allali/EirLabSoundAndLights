import os
import sys
filePath = os.path.dirname(os.path.dirname(__file__))
baseDirIdx = filePath.rfind("/")
sys.path.append("".join(filePath[:baseDirIdx]))
import light_configuration
import yaml
from yaml_manager import YamlWritter
import numpy as np
from typing import List





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
        
    

lights, _ = load_file(r"config/3D_coordinates_device.yml")


def dist(P1, P2):
    return np.sqrt(np.sum((P2-P1)**2))


def light_yaml_from_ring(center, radius:int, t0:int, rgbw:List[int], lightId, ym:YamlWritter):
    if radius == 0:
        return
    d = dist(center, lights[lightId])
    if d > radius:
        return
    ratio = (d / radius)**2
    #print(d, ratio, radius)


        
    color = rgbw * ratio
    ym.add(lightId, t0, color[0], color[1], color[2], color[3], 1)
    
def ring_appear(center, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:YamlWritter):
    timeInterval = 45
    times = np.arange(t0, t1, timeInterval)
    totalIterations = len(times) 
    for i, ti in enumerate(times[:-1]):
        for lightId in range(54):
            light_yaml_from_ring(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
    for lightId in range(54):
        light_yaml_from_ring(center, finalRadius, t1, rgbw, lightId, ym)


def light_yaml_from_circle(center, radius:int, t0:int, rgbw:List[int], lightId, ym:YamlWritter):
    if radius == 0:
        return
    d = dist(center, lights[lightId])
    if d > radius:
        return
    if d!=0:
        ratio = 1 - (d / radius)
    else: 
        ratio = 1
        
    color = rgbw * ratio
    ym.add(lightId, t0, color[0], color[1], color[2], color[3], 1)
    
def circle_appear(center, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:YamlWritter):
    timeInterval = 150
    times = np.arange(t0, t1, timeInterval)
    totalIterations = len(times) 
    for i, ti in enumerate(times):
        for lightId in range(54):
            light_yaml_from_circle(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
    for lightId in range(54):
        light_yaml_from_circle(center, finalRadius, t1, rgbw, lightId, ym)
            
def set_color(ym:YamlWritter, rgbw:List[int], t0:int, Tr:int=0):
    for lightId in range(54):
        ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], Tr)
            
    

    