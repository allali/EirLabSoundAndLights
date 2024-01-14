from typing import List
from math import sin, pi
from data_file_readers import utils

# 0 : LineIdentifier
# 1 : startTimeStamp
# 2 : endTimeStamp
# 3 : lightsId(s)

LINE_IDENTIFIER_ID = 0
START_TIME_STAMP_ID = 1
STOP_TIME_STAMP_ID = 2
LIGHT_IDS_ID = 3

ARGS_NUMBER = 4


def transcript_line(line:List[str], timeStep:int):
    check_data(line)

    timeStamps = utils.get_start_to_stop_time_stamps(line[START_TIME_STAMP_ID], line[STOP_TIME_STAMP_ID], timeStep)
    ids = utils.get_light_ids(line[LIGHT_IDS_ID])
    res = [[id, timeStamps[i//len(ids)], 0, 0, 0, 0] for i,id in enumerate(list(ids)*len(timeStamps))]
    for lightIdInSubList, lightId in enumerate(ids):
        rgbwList = get_rgbw_list(timeStamps, timeStep, lightId)
        for timeStampId in range(len(timeStamps)):
            listId = lightIdInSubList + timeStampId * len(ids)
            res[listId][2] = rgbwList[timeStampId][0]
            res[listId][3] = rgbwList[timeStampId][1]
            res[listId][4] = rgbwList[timeStampId][2]
            res[listId][5] = rgbwList[timeStampId][3]

    return res


def get_rgbw_list(timeStamps:List[int], timeStep:int, lightId:int):
    return [rainbow(timeStamp/timeStep + 3*lightId) for timeStamp in timeStamps]
    



def rainbow(i:int):
    t:float = pi * 2 * (i/1000)
    r:int = int( 255 * sin(t)**2 )
    g:int = int( 255 * sin(t + 0.33 * 2 * pi)**2 )
    b:int = int( 255 * sin(t + 0.66 * 2 * pi)**2 )
    w:int = 0
    return [r, g, b, w]



def check_data(line:List[str]):

    # Check for number of arguments in list
    if (len(line) != ARGS_NUMBER):
        raise Exception("Wrong number of statements for a slot_transition")

    # Check time stamps 
    utils.check_time_stamps(line[START_TIME_STAMP_ID])
    utils.check_time_stamps(line[STOP_TIME_STAMP_ID])
    if(int(line[START_TIME_STAMP_ID]) > int(line[STOP_TIME_STAMP_ID])):
        raise Exception("Start time stamp is greater than end time stamp")
    
    # Check light ids
    utils.check_light_ids(line[LIGHT_IDS_ID])
