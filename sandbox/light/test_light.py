import dmx
import time

universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("FT232R")

def set_line(lights,line,color):
    for l in lights.values():
        if l["line"]==line:
            l["light"].set_colour(color)


lights={}
for i in range(54):
    l=dmx.DMXLight4Slot(address=dmx.light.light_map[i])
    line=i%6
    column=int(i/6)
    lights[i]={"light":l,"x":line*2,"y":column*2,"line":line,"col":column}
    universe.add_light(l)

#lights=universe.get_lights()

for v in range(0,255,5):
    for l in lights.values():
        l["light"].set_colour(dmx.Color(0,0,v,0))
    interface.set_frame(universe.serialise())
    interface.send_update()
    time.sleep(0.01)

for l in range(6):
    set_line(lights,l,dmx.Color(255,0,0,0))
    interface.set_frame(universe.serialise())
    interface.send_update()

# applying a update take some time (about 30ms), thus for making 
# effect not depending on update time, better seems to add a time based
# system with a separate thread that apply changes as fast as possible

for l in lights.values():
    l["light"].set_colour(dmx.Color(200,200,200,50))
#    print(l)
    interface.set_frame(universe.serialise())
    interface.send_update()
#  time.sleep(0.5)
