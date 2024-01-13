from typing import List
import numpy as np

# 0 : LineIdentifier
# 1 : startTimeStamp
# 2 : endTimeStamp
# 3 : lightsId(s)
# 4 : Red
# 5 : Green
# 6 : Blue
# 7 : White

LINE_IDENTIFIER_ID = 0
START_TIME_STAMP_ID = 1
STOP_TIME_STAMP_ID = 2
LIGHT_IDS_ID = 3
RED_START_ID = 4
GREEN_START_ID = 5
BLUE_START_ID = 6
WHITE_START_ID = 7
RED_STOP_ID = 8
GREEN_STOP_ID = 9
BLUE_STOP_ID = 10
WHITE_STOP_ID = 11

ARGS_NUMBER = 12

def transcript_line(line:List[str], lineNumber:int, timeStep:int):
    check_data(line, lineNumber)

    timeStamps = get_time_stamps(line, timeStep)
    ids = get_light_ids(line)
    rgbwList = get_rgbw_list(line, timeStamps)


    return [[id, 
             timeStamps[i//len(ids)], 
             rgbwList[i//len(ids)][0], 
             rgbwList[i//len(ids)][1], 
             rgbwList[i//len(ids)][2], 
             rgbwList[i//len(ids)][3] 
             ] for i,id in enumerate(list(ids)*len(timeStamps))]


def get_time_stamps(line:List[str], timeStep:int):
    return list( np.arange( int(line[START_TIME_STAMP_ID]), int(line[STOP_TIME_STAMP_ID]), timeStep ) )

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

def get_rgbw_list(line:List[str], timeStamps:List[int]):
    sr, sg, sb, sw = get_start_rgbw(line)
    er, eg, eb, ew = get_stop_rgbw(line)
    return [[int(er+((sr-er)*(i/len(timeStamps)))),
             int(eg+((sg-eg)*(i/len(timeStamps)))),
             int(eb+((sb-eb)*(i/len(timeStamps)))),
             int(ew+((sw-ew)*(i/len(timeStamps))))] 
             for i in range(len(timeStamps)-1, -1, -1)]

def get_start_rgbw(line:List[str]):
    return list(map(int, line[RED_START_ID:WHITE_START_ID+1]))

def get_stop_rgbw(line:List[str]):
    return list(map(int, line[RED_STOP_ID:WHITE_STOP_ID+1]))


def check_data(line:List[str], lineNumber:int):

    # Check for number of arguments in list
    if (len(line) != ARGS_NUMBER):
        raise Exception(f"Error at line {lineNumber} in csv file.\nWrong number of statements for a slot_transition")

    # Check time stamps (arg 1 et 2)
    if (not(line[START_TIME_STAMP_ID].isdigit()) or not(line[STOP_TIME_STAMP_ID].isdigit())):
        raise Exception(f"Error at line {lineNumber} in csv file.\nTime stamps must be positive integers")
    elif(int(line[START_TIME_STAMP_ID]) > int(line[STOP_TIME_STAMP_ID])):
        raise Exception(f"Error at line {lineNumber} in csv file.\nStart time stamp is greater than end time stamp")
    
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
    for color in line[RED_START_ID:WHITE_STOP_ID+1]:
        if (not(color.isdigit()) or int(color) > 255):
            raise Exception(f"Error at line {lineNumber} in csv file.\nLight color is incorrect")
    for color in line[RED_STOP_ID:WHITE_STOP_ID+1]:
        if (not(color.isdigit()) or int(color) > 255):
            raise Exception(f"Error at line {lineNumber} in csv file.\nLight color is incorrect")
