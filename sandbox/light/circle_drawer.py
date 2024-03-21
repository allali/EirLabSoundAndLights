import yaml
from yaml_manager import yaml_writer
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
        
    

lights, _ = load_file(r"./yamls/3D_coordinates_device.yml")


def dist(P1, P2):
    return np.sqrt(np.sum((P2-P1)**2))


def light_yaml_from_ring(center, radius:int, t0:int, rgbw:List[int], lightId, ym:yaml_writer):
    if radius == 0:
        return
    d = dist(center, lights[lightId])
    if d > radius:
        return
    ratio = (d / radius)**2
    #print(d, ratio, radius)


        
    color = rgbw * ratio
    ym.add(lightId, t0, color[0], color[1], color[2], color[3], 1)
    
def ring_appear(center, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:yaml_writer):
    timeInterval = 45
    times = np.arange(t0, t1, timeInterval)
    totalIterations = len(times) 
    for i, ti in enumerate(times):
        for lightId in range(54):
            light_yaml_from_ring(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
    for lightId in range(54):
        light_yaml_from_ring(center, finalRadius, t1, rgbw, lightId, ym)


def light_yaml_from_circle(center, radius:int, t0:int, rgbw:List[int], lightId, ym:yaml_writer):
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
    
def circle_appear(center, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:yaml_writer):
    timeInterval = 150
    times = np.arange(t0, t1, timeInterval)
    totalIterations = len(times) 
    for i, ti in enumerate(times):
        for lightId in range(54):
            light_yaml_from_circle(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
    for lightId in range(54):
        light_yaml_from_circle(center, finalRadius, t1, rgbw, lightId, ym)
            
def set_color(ym:yaml_writer, rgbw:List[int], t0:int, Tr:int=0):
    for lightId in range(54):
        ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], Tr)
            
    

hg = np.array([-1,1.8, 2.5])
hd = np.array([-1,20, 2.5])
bg = np.array([15,1.8, 2.5])
bd = np.array([15,20, 2.5])
#center = np.array(lights[27])
radius = 15
t0= 0
t1 = 4870
t2 = 9440
t3 = 13922
tstop = 34000
bleu_clair = np.array([30, 100, 200, 12], dtype=np.uint8)
rouge = np.array([150, 20, 60, 40], dtype=np.uint8)
bleu = np.array([70, 160, 0, 12], dtype=np.uint8)
violet = np.array([100, 20, 150, 12], dtype=np.uint8)
vert = np.array([25,200,0,20], dtype=np.uint8)
rouge2 = np.array([240, 20, 60, 40], dtype=np.uint8)
rouge3 = np.array([255, 30, 70, 120], dtype=np.uint8)
yw1 = yaml_writer("test1")
yw2 = yaml_writer("test2")
yw3 = yaml_writer("test3")
yw4 = yaml_writer("test4")
set_color(yw1, [0,0,0,0], 0)
set_color(yw2, [0,0,0,0], 0)
set_color(yw3, [0,0,0,0], 0)
set_color(yw4, [0,0,0,0], 0)
circle_appear(hg, radius, t0, t0+1300, bleu_clair, yw1)
circle_appear(hd, radius, t1, t1+1300, rouge, yw2)
circle_appear(bg, radius, t2, t2+1300, bleu, yw3)
circle_appear(bd, radius, t3, t3+1300, violet, yw4)
set_color(yw1, [0,0,0,0], tstop-1000, 1)
set_color(yw2, [0,0,0,0], tstop-1000, 1)
set_color(yw3, [0,0,0,0], tstop-1000, 1)
set_color(yw4, [0,0,0,0], tstop-1000, 1)
set_color(yw1, [0,0,0,0], tstop, 1)
set_color(yw2, [0,0,0,0], tstop, 1)
set_color(yw3, [0,0,0,0], tstop, 1)
set_color(yw4, [0,0,0,0], tstop, 1)
yw1.write()
yw2.write()
yw3.write()
yw4.write()
del yw1, yw2, yw3, yw4



######### phase 2 ##############


yw5 = yaml_writer("ouverture")
set_color(yw5, [0,0,0,0], 0)
set_color(yw5, [0,0,0,0], 37370-45)
circle_appear((lights[27]+lights[26])/2, 40, 37370, 37800, rouge2, yw5)
set_color(yw5, [0,0,0,0], 56000)
yw5.write()
del yw5


########### Ring animation #############

yw6 = yaml_writer("rings")

set_color(yw6, [0,0,0,0], 0)

set_color(yw6, [0,0,0,0], 39320-50)
ring_appear(lights[12], 20, 39320, 39560, rouge3, yw6)
set_color(yw6, [0,0,0,0], 39790, 1)

set_color(yw6, [0,0,0,0], 40410-10)
ring_appear(lights[46], 20, 40410, 40710, rouge3, yw6)
set_color(yw6, [0,0,0,0], 41010, 1)

set_color(yw6, [0,0,0,0], 42650-10)
ring_appear(lights[10], 20, 42650, 42950, rouge3, yw6)
set_color(yw6, [0,0,0,0], 43350, 1)

ring_appear(lights[48], 20, 44400, 44900, rouge3, yw6)
set_color(yw6, [0,0,0,0], 45800, 1)

ring_appear(lights[27], 20, 46630, 47000, rouge3, yw6)
set_color(yw6, [0,0,0,0], 47400, 1)

set_color(yw6, [0,0,0,0], 47440, 1)
ring_appear(lights[27], 20, 47480, 47780, rouge3, yw6)
set_color(yw6, [0,0,0,0], 47900, 1)

ring_appear(lights[8], 20, 48200, 48750, rouge3, yw6)
set_color(yw6, [0,0,0,0], 49000, 1)

ring_appear(lights[8], 20, 48830, 49200, rouge3, yw6)
set_color(yw6, [0,0,0,0], 49600, 1)

yw6.write()
del yw6


