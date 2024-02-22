import dmx
import time

universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("TkinterDisplayer") # FT232R | Debug | Dummy


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
interface.send_update()

for v in range(0,256,1):
    lights[0]["light"].set_colour(dmx.Color(0,0,v,0))
    lights[1]["light"].set_colour(dmx.Color(0,0,v,255))
    interface.set_frame(universe.serialise())
    interface.send_update()
    time.sleep(0.03)

for v in range(0,256,1):
    lights[0]["light"].set_colour(dmx.Color(0,0,255,v))
    interface.set_frame(universe.serialise())
    interface.send_update()
    time.sleep(0.03)
lights[i]["light"].set_colour(dmx.Color(255,255,255,255))
    


# applying a update take some time (about 30ms), thus for making 
# effect not depending on update time, better seems to add a time based
# system with a separate thread that apply changes as fast as possible

for l in lights.values():
    l["light"].set_colour(dmx.Color(255,255,255,255))
interface.set_frame(universe.serialise())
interface.send_update()
#  time.sleep(0.5)
