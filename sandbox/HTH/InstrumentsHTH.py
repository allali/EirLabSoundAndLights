from yaml_manager import *
import time

class Instruments():
    def __init__(self,name):
        self.ymlFile = yaml_writer(name)

    def guitar(self,timing):
        duration = 2000
        self.ymlFile.round(timing,duration,255,153,51,100)
        self.ymlFile.round(timing + 2167,duration,232,72,67,100)
        self.ymlFile.round(timing + 4330,duration/2,232,232,186,100)
        self.ymlFile.round(timing + 5400, duration/2, 232,171,67,100)
        self.ymlFile.full_random(timing +6440, 0)
        self.ymlFile.full_random(timing + 6960, 0)
        self.ymlFile.full_random(timing + 7280, 0)
        self.ymlFile.full_change(timing + 7530 ,100,100,100,100,0)

    def drums(self,timing):
        neutral = 100
        self.ymlFile.column(5,timing + 250,neutral,neutral,neutral,neutral,0)
        self.ymlFile.column(2,timing +250 ,255,0,0,neutral,0)

        self.ymlFile.column(2,timing + 750,neutral,neutral,neutral,neutral,0)
        self.ymlFile.column(5,timing + 750, 255,0,0,neutral,0)
    
    def write(self):
        self.ymlFile.write()