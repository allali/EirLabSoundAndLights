import os
import sys

try:
    currentDir = os.path.dirname(os.path.abspath(__file__))
    repertoire_source = os.path.join(currentDir, r"../../")
    sys.path.append(repertoire_source)
    import config as cf
except:
    raise Exception("Path to config.py not found")

import tkinter as tk



class TkinterDisplayer:

    def __init__(self, windowSize = [727, 425]):
        self.nbLights = 54
        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.destroyDisplayer)
        self.windowClosed = False
        self.window.title("DMX Displayer")
        self.window.geometry(f"{windowSize[0]}x{windowSize[1]}")
        self.window.configure(bg="#555555")
        self.canvas = tk.Canvas(self.window, width=windowSize[0], height=windowSize[1])
        self.canvas.pack()
        self.lights = [[0,0,0,0] for i in range(self.nbLights)]
        self.lightsPositions = [[50 + 70 * (i//cf.number_of_columns), 70 * (i%cf.number_of_columns)] for i in range(self.nbLights)] 
        self.rectangles = [
            self.canvas.create_rectangle(
                self.lightsPositions[i][0] + 10, 
                self.lightsPositions[i][1] + 10, 
                self.lightsPositions[i][0] + 45, 
                self.lightsPositions[i][1] + 45, 
                fill="#FFFFFF",
                tags="light"
                ) for i in range(self.nbLights)
                ]
        self.lightIdToPos = [cf.light_map.index(i) for i in range(54)]
        self.draw_light_ids()
        

    def set_light_colors(self, colorList):
        if (not(self.windowClosed)):
            for i in range(self.nbLights):
                lightPos = self.lightIdToPos[self.nbLights-i-1]
                self.lights[lightPos][1] = colorList[i*4+1]
                self.lights[lightPos][2] = colorList[i*4+2]
                self.lights[lightPos][0] = colorList[i*4]
                self.lights[lightPos][3] = colorList[i*4+3]

    def draw_lights(self):
        for i in range(self.nbLights):
            color = self.rgbw_to_rgb(self.lights[i])
            rct = self.rectangles[i]
            self.canvas.itemconfig(rct, fill=color)
    
    def draw_light_ids(self):
        ypad = 46
        for i in range(self.nbLights):
            xpad = (18 if (self.nbLights-i-1 > 9) else 22)
            x= self.lightsPositions[i][0] + xpad
            y= self.lightsPositions[i][1] + ypad
            label = tk.Label(self.window, text=str(self.nbLights-i-1))
            label.place(x=x, y=y, anchor="nw")

    
    def update(self):
        if (not(self.windowClosed)):
            self.draw_lights()
            self.window.update()


        
    
    def rgbw_to_rgb(self, rgbw):
        """
        Convert rgbw colors to rgb ones. There isn't a good method to do that.
        Here you can either chose to convert rgbw into rgb using the vhite value or not.
        """
        convertUsingWhite = True

        if convertUsingWhite:
            r, g, b, w = rgbw
            rgbwRatio = .6

            r = r * rgbwRatio + w * (1-rgbwRatio)
            g = g * rgbwRatio + w * (1-rgbwRatio)
            b = b * rgbwRatio + w * (1-rgbwRatio)
            hexColor = "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))
        else:
            hexColor = "#{:02X}{:02X}{:02X}".format(int(rgbw[0]), int(rgbw[1]), int(rgbw[2]))

        return hexColor
        
    
    def close(self):
        if not(self.windowClosed):
            self.destroyDisplayer()

    def destroyDisplayer(self):
        self.window.destroy()
        self.windowClosed = True

        
                
if __name__ == "__main__": 
    a = TkinterDisplayer()
    import random as rd

    for i in range(10000):
        a.set_light_colors([[rd.randint(0, 255),rd.randint(0, 255),rd.randint(0, 255),rd.randint(0, 255)] for i in range(54)])
        a.update()
        a.window.update()
        


