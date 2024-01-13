from typing import List

# 0 : LineIdentifier
# 1 : timeStamp
# 2 : lightsId(s)
# 3 : Red
# 4 : Green
# 5 : Blue
# 6 : White

LINE_IDENTIFIER_ID = 0
START_TIME_STAMP_ID = 1
LIGHT_IDS_ID = 2
RED_ID = 3
GREEN_ID = 4
BLUE_ID = 5
WHITE_ID = 6

ARGS_NUMBER = 7

def transcript_line(line:List[str], lineNumber:int, timeStep:int):
    check_data(line, lineNumber)

    timeStamp = get_time_stamp(line)
    ids = get_light_ids(line)
    r, g, b, w = get_rgbw(line)

    return [[id, timeStamp, r, g, b, w] for id in ids]


def get_time_stamp(line:List[str]):
    return int(line[START_TIME_STAMP_ID])

def get_light_ids(line:List[str]):
    ids = set()
    for partedId in line[LIGHT_IDS_ID].split(";"):
        if ":" in partedId:
            startId, endId = list(map(int, partedId.split(":")))
            for id in range(startId, endId+1):
                ids.add(id)
        else:
            ids.add(int(partedId))
    return ids

def get_rgbw(line:List[str]):
    return list(map(int, line[RED_ID:WHITE_ID+1]))



def check_data(line:List[str], lineNumber:int):

    # Check for number of arguments in list
    if (len(line) != ARGS_NUMBER):
        raise Exception(f"Error at line {lineNumber} in csv file.\nWrong number of statements for a slot_transition")

    # Check time stamps (arg 1 et 2)
    if not(line[START_TIME_STAMP_ID].isdigit()):
        raise Exception(f"Error at line {lineNumber} in csv file.\nTime stamps must be positive integers")
    
    # Check light ids
    for partedId in line[LIGHT_IDS_ID].split(";"):
        if ":" in partedId:
            ids = partedId.split(":")
            if (len(ids) != 2 or not(ids[0].isdigit()) or not(ids[1].isdigit()) or int(ids[0] > ids[1])):
                raise Exception(f"Error at line {lineNumber} in csv file.\nLight id(s) are incorrect")
        else:
            if (not(partedId.isdigit())):
                raise Exception(f"Error at line {lineNumber} in csv file.\nLight id(s) are incorrect")
    
    # Check color values
    for color in line[RED_ID:WHITE_ID+1]:
        if (not(color.isdigit()) or int(color) > 255):
            raise Exception(f"Error at line {lineNumber} in csv file.\nLight color is incorrect")
