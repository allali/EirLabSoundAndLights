import os
import sys
filePath = os.path.dirname(os.path.dirname(__file__))
baseDirIdx = filePath.rfind("/")
sys.path.append("".join(filePath[:baseDirIdx]))
print(sys.path)
import config
import yaml
import yaml_manager 
import numpy as np
from typing import List

def read_yaml(file_name):
    try:
        with open(file_name, 'r') as file:
            
            data = yaml.safe_load(file)
            return data
    except (yaml.YAMLError, FileNotFoundError) as e:
        raise ValueError(f"Error reading YAML file: {e}")
    
def load_config_lights(file_name):
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
        
def load_timeline(file_name):
    data = read_yaml(file_name)
    print(data)
    if not isinstance(data, list):
        raise ValueError("Invalid YAML format. Expected a list.")

    try:
        meta_data = {}
        for meta in data[0]["meta"][0]:
            meta_data[meta] = data[0]["meta"][0][meta]

    except KeyError:
        meta_data = None
        print("No meta data in timeline")

    try:
        parts = {}
        for part in data[1]["parts"][0]:
            print(part)
            parts[part] = data[1]["parts"][0][part]
    except KeyError:
        parts = None
        print("No parts in timeline")
    
    try :
        events = {}
        for event in data[2]["events"][0]:
            events[event] = data[2]["events"][0][event]
    except KeyError:
        events = None
        print("No events in timeline")
    
    return (meta_data, parts, events)


# meta_data, parts, events = load_timeline(r"./yamls/feeling_good_timeline.yaml")



######### BEGINNING MAIN ##################
lights, _ = load_config_lights("config/3D_coordinates_device.yml")

import random
# generate random list of id of lights  with no duplicates
random_lights_id = random.sample(range(0, len(lights)), len(lights))
print(random_lights_id)

#add to yaml

ym = yaml_manager.YamlWritter('files/yamls/feeling_good/feeling_good.yaml')

# add on bpm 79
bpm = 79
time_per_beat = 60 / bpm
# print (parts)
intro_duration = 19
vocal_events = """ "birds":4383, "fly-":5000, "-ing":5240, "high":5390 , "you":5945, "know":6238, "how":6420, "I":6540, "feel":6895, "sun":10040, "in":10591, "the":10825, "sky":10920, "you":12000, "know":12385, "how":12600, "I":12900, "feel":13050, "breeze":16510, "drift-":17379,"-in":17695,"on":18110, "by":18463, "you":19030, "know":19110, "how":19370, "I":19570, "feel":19690, "it's":23040, "a":23260, "new":23430, "dawn":23730, "it's":24765, "a":25050, "new":25240, "day":25500, "it's":28195, "a":28466, "new":28590, "life":28740, "for":29590, "me":29940, "yeah":30493, "ouhou":37397,"""
coucou = [int(el[0]) for el in [elmt.split(',') for elmt in vocal_events.split(':')] if len(el) == 2]
# coucou is a var to retrieve words and the time code because i'm so smart that vocal_events is unusable
color_palette = ["FFE15D", "F49D1A", "DC3535", "B01E68"]
hex_to_rgb = lambda x: tuple(int(x[i:i+2], 16) for i in (0, 2, 4))
color_palette = [hex_to_rgb(x) for x in color_palette]
# during time of intro generate random color
# for i,time in enumerate(np.arange(1, intro_duration, time_per_beat)):
#     color_index = random.randint(0, len(color_palette)-1)
#     #ym.add(random_lights_id[i], time*1000+1000, np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255), 200, 1)
#     ym.add(random_lights_id[i], time*1000+3350, 0, 0, 0, 0, 0)
#     ym.add(random_lights_id[i], time*1000+4350+1000, color_palette[color_index][0], color_palette[color_index][1], color_palette[color_index][2], 0, 1)

# during time of vocal generate random color
print(coucou)
print(len(coucou))
#coucou without 2 last elements cause i don't want
coucou_random = coucou[:-2]
description__order = {}
for led in random_lights_id:
    ym.add(led, 0, 0, 0, 0, 0, 0)
for i, time in enumerate(coucou_random):
    print(i)
    color_index = random.randint(0, len(color_palette)-1)
    ym.add(random_lights_id[i], 
           time,
           color_palette[color_index][0], color_palette[color_index][1], color_palette[color_index][2], 0, 0)
    description__order[random_lights_id[i]] = color_palette[color_index]

# print(description__order)
#time of yeah in variable yeah
yeah = coucou[-2]

#time of ouhou in variable ouhou
ouhou = coucou[-1]

time_between_yeah_ouhou = ouhou - yeah
counter = 1000
#between yeah and ouhou generate vary white color using descrip
for led in random_lights_id:
    color_index = random.randint(0, len(color_palette)-1)
    ym.add(led, yeah-200, 0, 0, 0, 0, 1)
    ym.add(led, yeah, color_palette[color_index][0], color_palette[color_index][1], color_palette[color_index][2], 0, 1)

for i, order in description__order.items():
    if not counter >= time_between_yeah_ouhou:
        #random color from palette on 6 leds activated
        for j in range(6):
            if yeah+4000+counter >= yeah+time_between_yeah_ouhou:
                break
            else :
                led =random.randint(0,53)
                color_index = random.randint(0, len(color_palette)-1)
                ym.add(led, yeah + counter, color_palette[color_index][0], color_palette[color_index][1], color_palette[color_index][2], 0, 1)
                ym.add(led, yeah + counter+2000, order[0], order[1], order[2], 200, 1)
                ym.add(led, yeah + counter+4000,order[0], order[1], order[2], 0, 1)
                print(led)
            counter += 1000

for led in random_lights_id:
    color_index = random.randint(0, len(color_palette)-1)
    ym.add(led, ouhou, color_palette[color_index][0], color_palette[color_index][1], color_palette[color_index][2], 0, 1)
    ym.add(led, ouhou+2500, 0, 0, 0, 0, 1)
    ym.add(led, ouhou+5000, 0, 0, 0, 0, 0)
    if led == 3:
        print("yaya",led, ouhou+2500)
        print("yoyo",led, ouhou+5000)


instrument= 43270
instrument2 = 44508
instrument3 = 44823
instrument4 = 46038
instrument5 = 46343
instrument6 = 47568
instrument7 = 47870
instrument8 = 48350
instrument9 = 48621
instrument10 = 48905
instrument11 = 49128
instrument12 = 49380
import circle_drawer
center = (lights[26]+lights[27])/2
print(center)
circle_drawer.ring_appear(center, 30, instrument-200, instrument+800, np.array([255, 255, 255, 0]), ym)
# circle_drawer.ring_appear(center, 30, instrument2, instrument2+500, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument2-20, 216, 192, 245, 0, 0)
    ym.add(i, instrument2+50, 0, 0, 0, 0, 0)

circle_drawer.ring_appear(center, 30, instrument3-200, instrument3+600, np.array([216, 192, 245, 0]), ym)
# circle_drawer.ring_appear(center, 30, instrument4, instrument4+500, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument4-20, 203, 234, 216, 0, 0)
    ym.add(i, instrument4+50, 0, 0, 0, 0, 0)
circle_drawer.ring_appear(center, 30, instrument5-200, instrument5+600, np.array([203, 234, 216, 0]), ym)
# circle_drawer.ring_appear(center, 30, instrument6, instrument6+500, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument6-20, 185, 225, 252, 0, 0)
    ym.add(i, instrument6+50, 0, 0, 0, 0, 0)
circle_drawer.ring_appear(center, 30, instrument7-200, instrument7+300, np.array([185, 225, 252, 0]), ym)
# circle_drawer.ring_appear(center, 30, instrument8, instrument8+400, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument8-20, 255, 182, 193, 0, 0)
    ym.add(i, instrument8+50, 0, 0, 0, 0, 0)
# circle_drawer.ring_appear(center, 30, instrument9, instrument9+400, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument9-20, 255, 182, 193, 0, 0)
    ym.add(i, instrument9+50, 0, 0, 0, 0, 0)
# circle_drawer.ring_appear(center, 30, instrument10, instrument10+400, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument10-20, 255, 182, 193, 0, 0)
    ym.add(i, instrument10+50, 0, 0, 0, 0, 0)
# circle_drawer.ring_appear(center, 30, instrument11, instrument11+400, np.array([255, 255, 255, 0]), ym)
for i in range(54):
    ym.add(i, instrument11-20, 255, 182, 193, 0, 0)
    ym.add(i, instrument11+50, 0, 0, 0, 0, 0)

circle_drawer.ring_appear(center, 30, instrument12-200, instrument12+850, np.array([255, 182, 193, 0]), ym)
ym.write()
