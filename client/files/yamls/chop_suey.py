from yaml_manager import *
import os


if __name__ == "__main__":
    #os.remove("chop_suey.yaml")
    yw = yaml_writer("chop_suey")
    yw.full_change(500, 255, 255, 255, 255, 1)
    yw.column(1,1500,255, 0, 0, 100, 0)
    yw.column(2,2500,255, 0, 0, 100, 0)
    yw.column(3,3500,255, 0, 0, 100, 0)
    yw.column(4,4500,255, 0, 0, 100, 0)
    yw.column(5,5500,255, 0, 0, 100, 0)
    yw.column(6,6500,255, 0, 0, 100, 0)
    yw.full_change(8000,0,0,255,100,0)
    yw.full_change(12000,0,204,102,100,1)
    yw.full_change(15000,255,153, 51, 100, 1)
    yw.full_change(15500,102,178,255,100,0)
    yw.full_change(16900,255,255,0,100,1)
    yw.full_change(17000,255,128,0,100,0)
    yw.full_change(24000,0,204,0,100,1)
    yw.full_change(30000,0,76,153,100,1)
    yw.spiral(30100,10000,255,0,0,100)

    yw.write()

