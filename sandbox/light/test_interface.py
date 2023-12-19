import dmx
import time

universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("FT232R") # FT232R | Debug | Dummy
interface2 = dmx.DMXInterface("TkinterDisplayer") 


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
for l in lights.values():
    l["light"].set_colour(dmx.Color(255,255,255,255))
interface.set_frame(universe.serialise())
interface2.set_frame(universe.serialise())
interface.send_update()
interface2.send_update()
for i in range(54):
    
    lights[i]["light"].set_colour(dmx.Color(0,0,255,0))
    interface.set_frame(universe.serialise())
    interface2.set_frame(universe.serialise())
    interface.send_update()
    interface2.send_update()
    time.sleep(0.08)
    lights[i]["light"].set_colour(dmx.Color(255,255,255,255))
    


# applying a update take some time (about 30ms), thus for making 
# effect not depending on update time, better seems to add a time based
# system with a separate thread that apply changes as fast as possible
time.sleep(4)
for l in lights.values():
    l["light"].set_colour(dmx.Color(255,255,255,255))
interface.set_frame(universe.serialise())
interface2.set_frame(universe.serialise())
interface.send_update()
interface2.send_update()
#  time.sleep(0.5)
