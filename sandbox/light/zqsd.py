import dmx
import time
import tkinter as tk
import bindings

tcl = tk.Tcl()
universe = dmx.DMXUniverse()
interface = dmx.DMXInterface("TkinterDisplayer")

lights={}
for i in range(54):
    l=dmx.DMXLight4Slot(address=dmx.light.light_map[i])
    line=i%6
    column=int(i/6)
    lights[i]={"light":l,"x":line*2,"y":column*2,"line":line,"col":column}
    universe.add_light(l)

#interface._devicebind('z', lambda event=None: test())

def test():
    print("bonjour")


lights[0]["light"].set_colour(dmx.Color(0,0,255))
interface.set_frame(universe.serialise())
interface.send_update()

bindings.set_bindings(lights, interface, universe)

tcl.mainloop()