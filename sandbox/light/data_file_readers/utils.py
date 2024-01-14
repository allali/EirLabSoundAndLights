import numpy as np

    
def check_time_stamps(field:str):
    if not(field.isdigit()):
        raise Exception("Time stamps must be positive integers")
    
def check_light_ids(field:str):
    for partedId in field.split(";"):
        if ":" in partedId:
            ids = partedId.split(":")
            if (len(ids) != 2 or not(ids[0].isdigit()) or not(ids[1].isdigit()) or int(ids[0]) > int(ids[1])):
                raise Exception("Light id(s) are incorrect")
        else:
            if (not(partedId.isdigit())):
                raise Exception("Light id(s) are incorrect")
            
def check_light_color_values(field:str):
    if (not(field.isdigit()) or int(field) > 255):
        raise Exception("Light color is incorrect")
    

def get_light_ids(field:str):
    ids = set()
    for partedId in field.split(";"):
        if ":" in partedId:
            startId, endId = list(map(int, partedId.split(":")))
            for id in range(startId, endId+1):
                ids.add(id)
        else:
            ids.add(int(partedId))
    return ids

def get_start_to_stop_time_stamps(startField:str, stopField, timeStep:int):
    return list( np.arange( int(startField), int(stopField), timeStep ) )