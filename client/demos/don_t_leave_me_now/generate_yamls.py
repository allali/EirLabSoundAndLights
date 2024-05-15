import os
import sys
MAIN_FOLDER = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(MAIN_FOLDER)
from light import YamlWritter, YamlEffectWritter, lightConfig, MergeType
import numpy as np
import time

hg = np.array([-1,1.8, 2.5])
hd = np.array([-1,20, 2.5])
bg = np.array([15,1.8, 2.5])
bd = np.array([15,20, 2.5])
#center = np.array(lightConfig.LIGHTS_COORDINATES[27])
radius = 15
t0= 0
t1 = 4870
t2 = 9440
t3 = 13922
tstop = 34000
bleu_clair = np.array([30, 100, 200, 12], dtype=np.uint8)
rouge = np.array([150, 20, 60, 40], dtype=np.uint8)
bleu = np.array([70, 160, 0, 12], dtype=np.uint8)
violet = np.array([100, 20, 150, 12], dtype=np.uint8)
vert = np.array([25,200,0,20], dtype=np.uint8)
rouge2 = np.array([240, 20, 60, 40], dtype=np.uint8)
rouge3 = np.array([255, 30, 70, 120], dtype=np.uint8)
yw1 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_1.yaml")
yw2 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_2.yaml")
yw3 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_3.yaml")
yw4 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_4.yaml")
YamlEffectWritter.set_color(yw1, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw2, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw3, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw4, [0,0,0,0], 0)
YamlEffectWritter.draw_circle(hg, radius, t0, t0+1300, bleu_clair, yw1)
YamlEffectWritter.draw_circle(hd, radius, t1, t1+1300, rouge, yw2)
YamlEffectWritter.draw_circle(bg, radius, t2, t2+1300, bleu, yw3)
YamlEffectWritter.draw_circle(bd, radius, t3, t3+1300, violet, yw4)
YamlEffectWritter.set_color(yw1, [0,0,0,0], tstop-1000, 1)
YamlEffectWritter.set_color(yw2, [0,0,0,0], tstop-1000, 1)
YamlEffectWritter.set_color(yw3, [0,0,0,0], tstop-1000, 1)
YamlEffectWritter.set_color(yw4, [0,0,0,0], tstop-1000, 1)
YamlEffectWritter.set_color(yw1, [0,0,0,0], tstop, 1)
YamlEffectWritter.set_color(yw2, [0,0,0,0], tstop, 1)
YamlEffectWritter.set_color(yw3, [0,0,0,0], tstop, 1)
YamlEffectWritter.set_color(yw4, [0,0,0,0], tstop, 1)
yw1.write()
yw2.write()
yw3.write()
yw4.write()
del yw1, yw2, yw3, yw4



######### phase 2 ##############


yw5 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_5.yaml")
YamlEffectWritter.set_color(yw5, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw5, [0,0,0,0], 37370-45)
YamlEffectWritter.draw_circle((lightConfig.LIGHTS_COORDINATES[27]+lightConfig.LIGHTS_COORDINATES[26])/2, 40, 37370, 37800, rouge2, yw5)
YamlEffectWritter.set_color(yw5, [0,0,0,0], 56000)
yw5.write()
del yw5


########### Ring animation #############

yw6 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_6.yaml")

YamlEffectWritter.set_color(yw6, [0,0,0,0], 0)

YamlEffectWritter.set_color(yw6, [0,0,0,0], 39320-50)
YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[12], 20, 39320, 39560, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 39790, 1)

YamlEffectWritter.set_color(yw6, [0,0,0,0], 40410-27)
YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[46], 20, 40410, 40710, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 41010, 1)

YamlEffectWritter.set_color(yw6, [0,0,0,0], 42650-27)
YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[10], 20, 42650, 42950, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 43350, 1)

YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[48], 20, 44400, 44900, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 45800, 1)

YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[27], 20, 46630, 47000, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 47400, 1)

YamlEffectWritter.set_color(yw6, [0,0,0,0], 47440, 1)
YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[27], 20, 47480, 47780, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 47900, 1)

YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[8], 20, 48200, 48750, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 48800, 1)

YamlEffectWritter.draw_ring(lightConfig.LIGHTS_COORDINATES[8], 20, 48830, 49200, rouge3, yw6)
YamlEffectWritter.set_color(yw6, [0,0,0,0], 49600, 1)

yw6.write()
del yw6


#############################################


s1 = lightConfig.LIGHTS_COORDINATES[53]
s2 = lightConfig.LIGHTS_COORDINATES[5]
s3 = lightConfig.LIGHTS_COORDINATES[0]
s4 = lightConfig.LIGHTS_COORDINATES[48]
dim = [3,3.2]
dim2 = [3,4.2]
#center = np.array(lightConfig.LIGHTS_COORDINATES[27])
radius = 15
t0= 18600
t1 = 22980
t2 = 27300
t3 = 31700
t4 = 32000
tf=34000
bleu_clair = np.array([30, 100, 200, 12], dtype=np.uint8)
rouge = np.array([150, 20, 60, 40], dtype=np.uint8)
rouge2 = np.array([240, 20, 60, 40], dtype=np.uint8)
bleu = np.array([70, 160, 0, 12], dtype=np.uint8)
violet = np.array([100, 20, 150, 12], dtype=np.uint8)
vert = np.array([25,200,0,20], dtype=np.uint8)
jaune = np.array([240, 200, 60, 40])
blancw = np.array([0,0,0,210], dtype=np.uint8)
noir = np.array([0,0,0,0], dtype=np.uint8)

yw1 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_7.yaml")

YamlEffectWritter.set_color(yw1, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw1, [0,0,0,0], t0-45)

YamlEffectWritter.draw_rectangle(s1, s2, dim, t0, t1-27, bleu_clair, yw1)
YamlEffectWritter.draw_rectangle(s2, s3, dim2, t1, t2-27, bleu_clair, yw1)
YamlEffectWritter.draw_rectangle(s3, s4, dim, t2, t3-27, bleu_clair, yw1)
#YamlEffectWritter.draw_rectangle(s4, s1, dim, t3, t4, bleu_clair, yw1)

YamlEffectWritter.set_color(yw1, [0,0,0,0], tf, 1)
YamlEffectWritter.set_color(yw1, [0,0,0,0], tf+2000,1)

yw1.write()
del yw1

########################################################
yw2 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_8.yaml")

YamlEffectWritter.set_color(yw2, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw2, [0,0,0,0], t0-45)

YamlEffectWritter.draw_rectangle(s2, s3, dim2, t0, t1-27, rouge, yw2)
YamlEffectWritter.draw_rectangle(s3, s4, dim, t1, t2-27, rouge, yw2)
YamlEffectWritter.draw_rectangle(s4, s1, dim, t2, t3-27, rouge, yw2)
#YamlEffectWritter.draw_rectangle(s1, s2, dim, t3, t4, rouge, yw2)

YamlEffectWritter.set_color(yw2, [0,0,0,0], tf,1)
YamlEffectWritter.set_color(yw2, [0,0,0,0], tf+2000,1)

yw2.write()
del yw2

########################################################
yw3 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_9.yaml")

YamlEffectWritter.set_color(yw3, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw3, [0,0,0,0], t0-45)

YamlEffectWritter.draw_rectangle(s3, s4, dim, t0, t1-27, bleu, yw3)
YamlEffectWritter.draw_rectangle(s4, s1, dim, t1, t2-27, bleu, yw3)
YamlEffectWritter.draw_rectangle(s1, s2, dim, t2, t3-27, bleu, yw3)
#YamlEffectWritter.draw_rectangle(s2, s3, dim, t3, t4, bleu, yw3)

YamlEffectWritter.set_color(yw3, [0,0,0,0], tf,1)
YamlEffectWritter.set_color(yw3, [0,0,0,0], tf+2000,1)

yw3.write()
del yw3

########################################################
yw4 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_10.yaml")

YamlEffectWritter.set_color(yw4, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw4, [0,0,0,0], t0-45)

YamlEffectWritter.draw_rectangle(s4, s1, dim, t0, t1-27, violet, yw4)
YamlEffectWritter.draw_rectangle(s1, s2, dim, t1, t2-27, violet, yw4)
YamlEffectWritter.draw_rectangle(s2, s3, dim2, t2, t3-27, violet, yw4)
#YamlEffectWritter.draw_rectangle(s3, s4, dim, t3, t4, violet, yw4)

YamlEffectWritter.set_color(yw4, [0,0,0,0], tf,1)
YamlEffectWritter.set_color(yw4, [0,0,0,0], tf+2000,1)

yw4.write()
del yw4


#################### SAXOPHONE ################################

tsax = 54732
tfsax = 55489
tffsax = 80000

yw5 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_11.yaml")

dimSax = np.array([50, 2.5])
YamlEffectWritter.set_color(yw5, [0,0,0,0], 0)
YamlEffectWritter.set_color(yw5, [0,0,0,0], tsax-27)

YamlEffectWritter.draw_rectangle(lightConfig.LIGHTS_COORDINATES[3], lightConfig.LIGHTS_COORDINATES[51], dimSax, tsax, tfsax, vert, yw5, 60)
YamlEffectWritter.set_color(yw5, jaune, 56000, 1)

YamlEffectWritter.set_color(yw5, np.array([240, 10, 140, 40]) , 59000, 1)
YamlEffectWritter.set_color(yw5, vert, 62000, 1)
YamlEffectWritter.set_color(yw5, rouge2, 64000, 1)
YamlEffectWritter.set_color(yw5, rouge, 67000, 1)
YamlEffectWritter.set_color(yw5, bleu_clair, 71000, 1)
YamlEffectWritter.set_color(yw5, violet, 71027, 1)
YamlEffectWritter.set_color(yw5, jaune, 73000, 1)

YamlEffectWritter.set_color(yw5, [0,0,0,0], tffsax)

yw5.write()
del yw5


################### BATTERIE ###############################


times = [51015, 51844, 52645, 53460, 53745, 54532, 54775]

yw6 = YamlWritter("demos/don_t_leave_me_now/dtmn_fragment_12.yaml")
YamlEffectWritter.set_color(yw6, [0,0,0,0], 0)    

for t in times:
    YamlEffectWritter.set_color(yw6, noir, t-90)
    YamlEffectWritter.set_color(yw6, blancw, t, 1)
    YamlEffectWritter.set_color(yw6, noir, t+90)
    
yw6.write()
del yw6

names = [MAIN_FOLDER + "/demos/don_t_leave_me_now/dtmn_fragment_" + str(i) + ".yaml" for i in range(1,13)]
YamlWritter.merge_yamls(names, "files/yamls/dtmn.yaml", 54, MergeType.MAX)

for filename in names:
    os.remove(filename)