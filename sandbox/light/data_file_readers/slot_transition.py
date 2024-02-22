from typing import List
from data_file_readers import utils

# 0 : LineIdentifier
# 1 : timeStamp
# 2 : lightsId(s)
# 3 : Color

LINE_IDENTIFIER_ID = 0
START_TIME_STAMP_ID = 1
LIGHT_IDS_ID = 2
COLOR_ID = 3

ARGS_NUMBER = 4

def transcript_line(line:List[str], timeStep:int):
    check_data(line)

    timeStamp = get_time_stamp(line)
    ids = utils.get_light_ids(line[LIGHT_IDS_ID])
    r, g, b, w = utils.get_light_color_values(line[COLOR_ID])

    return [[id, timeStamp, r, g, b, w] for id in ids]


def get_time_stamp(line:List[str]):
    return int(line[START_TIME_STAMP_ID])



def check_data(line:List[str]):

    # Check for number of arguments in list
    if (len(line) != ARGS_NUMBER):
        raise Exception("Wrong number of statements for a slot_transition")

    # Check time stamps 
    utils.check_time_stamps(line[START_TIME_STAMP_ID])
    
    # Check light ids
    utils.check_light_ids(line[LIGHT_IDS_ID])

    # Check color values
    utils.check_light_color_values(line[COLOR_ID])
