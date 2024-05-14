from yaml_manager import *
import os


if __name__ == "__main__":    

    yw = yaml_writer("chop_suey2")

    yw.full_change(41000,255,128,0,100,0)
    yw.full_change(42000,255,0,0,100,0)
    yw.full_change(43000,255,128,0,100,0)
    yw.full_change(44000,255,255,0,100,0)
    yw.full_change(45000,102,0,102,100,0)
    yw.full_change(45900,0,0,0,0,1)
    yw.full_change(46000,0,0,153,0,0)
    yw.full_change(47000,153,0,153,0,1)
    yw.full_change(47800,0,0,0,0,1)
    yw.full_change(47900,255,128,0,128,0)
    yw.full_change(48400,0,0,255,128,0)
    yw.full_change(49100,255,128,0,128,0)
    yw.full_change(49800,0,0,0,0,1)
    yw.full_change(49850,0,0,255,128,0)
    yw.full_change(51000,0,0,0,0,0)
    yw.full_change(51700,255,128,0,1,0)
    yw.wave_column(51800,1100,0,0,255,128,255,0,0,128)
    for i in range(13):
        yw.full_change(52300+i*500,(64*i)//256,(128+128*i)//256, (128*i)//256, 128, 0)
    
    yw.write()