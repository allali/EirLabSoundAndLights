


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



def light_yaml_from_rectangle(center, dimensions:List[int], t0:int, rgbw:List[int], lightId, ym:yaml_writer):
    dh = abs(center[0] - lights[lightId][0])
    dl = abs(center[1] - lights[lightId][1])
    

    if (dh < dimensions[0] and dl < dimensions[1]):
        ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], 1)
    
    
def rectangle_appear(start, stop, dimensions:int, t0:int, t1:int, rgbw:List[int], ym:yaml_writer, precision=200):
    timeInterval = precision
    times = np.arange(t0, t1, timeInterval)
    totalIterations = len(times) 
    for i, ti in enumerate(times):
        for lightId in range(54):
            light_yaml_from_rectangle(start + i*(stop-start)/totalIterations, dimensions, ti, rgbw.astype(np.uint8), lightId, ym)
    for lightId in range(54):
        light_yaml_from_rectangle(stop, dimensions, t1, rgbw, lightId, ym)
            
def set_color(ym:yaml_writer, rgbw:List[int], t0:int, Tr:int=0):
    for lightId in range(54):
        ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], Tr)
        

s1 = lights[53]
s2 = lights[5]
s3 = lights[0]
s4 = lights[48]
dim = [3,3.2]
dim2 = [3,4.2]
#center = np.array(lights[27])
radius = 15
t0= 18600
t1 = 22980
t2 = 27300
t3 = 31700
t4 = 32000
tf=34000
bleu_clair = np.array([30, 100, 200, 12], dtype=np.uint8)
rouge = np.array([150, 20, 60, 40], dtype=np.uint8)
rouge2 = np.array([240, 20, 60, 40], dtype=np.uint8)
bleu = np.array([70, 160, 0, 12], dtype=np.uint8)
violet = np.array([100, 20, 150, 12], dtype=np.uint8)
vert = np.array([25,200,0,20], dtype=np.uint8)
jaune = np.array([240, 200, 60, 40])
blancw = np.array([0,0,0,210], dtype=np.uint8)
noir = np.array([0,0,0,0], dtype=np.uint8)

yw1 = yaml_writer("rect1")

set_color(yw1, [0,0,0,0], 0)
set_color(yw1, [0,0,0,0], t0-45)

rectangle_appear(s1, s2, dim, t0, t1, bleu_clair, yw1)
rectangle_appear(s2, s3, dim2, t1, t2, bleu_clair, yw1)
rectangle_appear(s3, s4, dim, t2, t3, bleu_clair, yw1)
#rectangle_appear(s4, s1, dim, t3, t4, bleu_clair, yw1)

set_color(yw1, [0,0,0,0], tf, 1)
set_color(yw1, [0,0,0,0], tf+2000,1)

yw1.write()
del yw1

########################################################
yw2 = yaml_writer("rect2")

set_color(yw2, [0,0,0,0], 0)
set_color(yw2, [0,0,0,0], t0-45)

rectangle_appear(s2, s3, dim2, t0, t1, rouge, yw2)
rectangle_appear(s3, s4, dim, t1, t2, rouge, yw2)
rectangle_appear(s4, s1, dim, t2, t3, rouge, yw2)
#rectangle_appear(s1, s2, dim, t3, t4, rouge, yw2)

set_color(yw2, [0,0,0,0], tf,1)
set_color(yw2, [0,0,0,0], tf+2000,1)

yw2.write()
del yw2

########################################################
yw3 = yaml_writer("rect3")

set_color(yw3, [0,0,0,0], 0)
set_color(yw3, [0,0,0,0], t0-45)

rectangle_appear(s3, s4, dim, t0, t1, bleu, yw3)
rectangle_appear(s4, s1, dim, t1, t2, bleu, yw3)
rectangle_appear(s1, s2, dim, t2, t3, bleu, yw3)
#rectangle_appear(s2, s3, dim, t3, t4, bleu, yw3)

set_color(yw3, [0,0,0,0], tf,1)
set_color(yw3, [0,0,0,0], tf+2000,1)

yw3.write()
del yw3

########################################################
yw4 = yaml_writer("rect4")

set_color(yw4, [0,0,0,0], 0)
set_color(yw4, [0,0,0,0], t0-45)

rectangle_appear(s4, s1, dim, t0, t1, violet, yw4)
rectangle_appear(s1, s2, dim, t1, t2, violet, yw4)
rectangle_appear(s2, s3, dim2, t2, t3, violet, yw4)
#rectangle_appear(s3, s4, dim, t3, t4, violet, yw4)

set_color(yw4, [0,0,0,0], tf,1)
set_color(yw4, [0,0,0,0], tf+2000,1)

yw4.write()
del yw4


#################### SAXOPHONE ################################

tsax = 54732
tfsax = 55489
tffsax = 80000

yw5 = yaml_writer("saxo")

dimSax = np.array([50, 2.5])
set_color(yw5, [0,0,0,0], 0)
set_color(yw5, [0,0,0,0], tsax)

rectangle_appear(lights[3], lights[51], dimSax, tsax, tfsax, vert, yw5, 60)
set_color(yw5, jaune, 56000, 1)

set_color(yw5, np.array([240, 10, 140, 40]) , 59000, 1)
set_color(yw5, vert, 62000, 1)
set_color(yw5, rouge2, 64000, 1)
set_color(yw5, rouge, 67000, 1)
set_color(yw5, bleu_clair, 71000, 1)
set_color(yw5, violet, 71000, 1)
set_color(yw5, jaune, 73000, 1)

set_color(yw5, [0,0,0,0], tffsax)

yw5.write()
del yw5


################### BATTERIE ###############################


times = [51015, 51844, 52645, 53460, 53745, 54532, 54775]

yw6 = yaml_writer("drums")
set_color(yw6, [0,0,0,0], 0)

for t in times:
    set_color(yw6, noir, t-90)
    set_color(yw6, blancw, t, 1)
    set_color(yw6, noir, t+90)
    
yw6.write()
del yw6