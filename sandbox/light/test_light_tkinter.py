import dmx
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import colorchooser
tcl = tk.Tcl()
print(tcl.call("info", "patchlevel"))
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


root = tk.Tk()
root.title("DMX Light Controller")
root.geometry("500x500")

def chooseColor():
    color_code = colorchooser.askcolor(title="Choose color")
    print(color_code)
    for l in lights.values():
        l["light"].set_colour(dmx.Color(int(color_code[0][0]),int(color_code[0][1]),int(color_code[0][2]),200))
    interface.set_frame(universe.serialise())
    interface.send_update()

def setBlueInstant():
    for v in range(0,255,5):
        for l in lights.values():
            l["light"].set_colour(dmx.Color(0,0,v,0))
        interface.set_frame(universe.serialise())
        interface.send_update()

def setRedLine():
    for l in range(6):
        set_line(lights,l,dmx.Color(255,0,0,0))
        interface.set_frame(universe.serialise())
        interface.send_update()
def setNormalWhite():
    for l in lights.values():
        l["light"].set_colour(dmx.Color(200,200,200,200))
    interface.set_frame(universe.serialise())
    interface.send_update()

setBlueInstantButton = tk.Button(root, text ="All Blue Instant", command = setBlueInstant)
setRedLineButton = tk.Button(root, text ="All Red Line", command = setRedLine)
setNormalWhiteButton = tk.Button(root, text ="All Normal White", command = setNormalWhite)
chooseColorButton = tk.Button(root, text ="Choose Color", command = chooseColor)

chooseColorButton.place(x = 50,y = 200)
setNormalWhiteButton.place(x = 50,y = 150)
setBlueInstantButton.place(x = 50,y = 50)
setRedLineButton.place(x = 50,y = 100)
root.mainloop()