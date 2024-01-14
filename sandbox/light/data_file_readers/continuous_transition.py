from typing import List
from data_file_readers import utils

# 0 : LineIdentifier
# 1 : startTimeStamp
# 2 : endTimeStamp
# 3 : lightsId(s)
# 4 : Color at start of transition
# 5 : Color at end of transition

LINE_IDENTIFIER_ID = 0
START_TIME_STAMP_ID = 1
STOP_TIME_STAMP_ID = 2
LIGHT_IDS_ID = 3
COLOR_START_ID = 4
COLOR_STOP_ID = 5

ARGS_NUMBER = 6

def transcript_line(line:List[str], timeStep:int):
    check_data(line)

    timeStamps = utils.get_start_to_stop_time_stamps(line[START_TIME_STAMP_ID], line[STOP_TIME_STAMP_ID], timeStep)
    ids = utils.get_light_ids(line[LIGHT_IDS_ID])
    rgbwList = get_rgbw_list(line, timeStamps)


    return [[id, 
             timeStamps[i//len(ids)], 
             rgbwList[i//len(ids)][0], 
             rgbwList[i//len(ids)][1], 
             rgbwList[i//len(ids)][2], 
             rgbwList[i//len(ids)][3] 
             ] for i,id in enumerate(list(ids)*len(timeStamps))]


def get_rgbw_list(line:List[str], timeStamps:List[int]):
    sr, sg, sb, sw = utils.get_light_color_values(line[COLOR_START_ID])
    er, eg, eb, ew = utils.get_light_color_values(line[COLOR_STOP_ID])
    return [[int(er+((sr-er)*(i/len(timeStamps)))),
             int(eg+((sg-eg)*(i/len(timeStamps)))),
             int(eb+((sb-eb)*(i/len(timeStamps)))),
             int(ew+((sw-ew)*(i/len(timeStamps))))] 
             for i in range(len(timeStamps)-1, -1, -1)]


def check_data(line:List[str]):

    # Check for number of arguments in list
    if (len(line) != ARGS_NUMBER):
        raise Exception("Wrong number of statements for a slot_transition")

    # Check time stamps (arg 1 et 2)
    utils.check_time_stamps(line[START_TIME_STAMP_ID])
    utils.check_time_stamps(line[STOP_TIME_STAMP_ID])
    if(int(line[START_TIME_STAMP_ID]) > int(line[STOP_TIME_STAMP_ID])):
        raise Exception("Start time stamp is greater than end time stamp")
    
    # Check light ids
    utils.check_light_ids(line[LIGHT_IDS_ID])
    
    # Check color values
    utils.check_light_color_values(line[COLOR_START_ID])
    utils.check_light_color_values(line[COLOR_STOP_ID])
