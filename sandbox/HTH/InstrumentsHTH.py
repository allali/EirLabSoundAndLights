from yaml_manager import *
import time

class Instruments():
    def __init__(self,name):
        self.ymlFile = yaml_writer(name)

    def guitar(self,timing):
        duration = 2000
        basic_color = 100
        timings= [0,2167,4330,5400]
        color = [[255,153,51,basic_color],[232,72,67,basic_color],[232,232,186,basic_color],[232,171,67,basic_color]]
        for i in range(len(timings)):
            self.ymlFile.round_cst_1_row(timing + timings[i],color[i][0],color[i][1],color[i][2],color[i][3])
            self.ymlFile.round_cst_1_row(timing + timings[i] + 330/(1+i//2),basic_color,basic_color,basic_color,basic_color)
            self.ymlFile.round_cst_2_row(timing + timings[i] + 330/(1+i//2),color[i][0],color[i][1],color[i][2],color[i][3])
            self.ymlFile.round_cst_2_row(timing + timings[i] + 660/(1+i//2),basic_color,basic_color,basic_color,basic_color)
            self.ymlFile.round_cst_1_row(timing + timings[i] + 660/(1+i//2),color[i][0],color[i][1],color[i][2],color[i][3])
            self.ymlFile.round_cst_1_row(timing + timings[i] + 990/(1+i//2) ,basic_color,basic_color,basic_color,basic_color)

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

    def build(self,timing):
        incr = 0
        for k in range(12):
            self.ymlFile.full_change(timing + incr,100,100,100,100,0)
            incr+= 125
            self.ymlFile.full_change(timing + incr,100,100,100,255,0)
            incr+= 125
    
    def zero(self,timing):
        self.ymlFile.full_change(timing,100,100,100,100,0)

    def random_period(self,timing,period,number):
        for k in range(number):
            self.ymlFile.full_random(timing + period * k,0)
            self.ymlFile.full_random(timing + period * k + 250,0)
            

    def full_change(self,timing):
        self.ymlFile.full_change(timing,100,100,100,100,0)
        self.ymlFile.full_change(timing,100,100,100,255,0)
        self.ymlFile.full_change(timing+250,100,100,100,100,0)
        self.ymlFile.full_change(timing+250,100,100,100,255,0)

