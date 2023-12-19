import tkinter as tk
import os
import sys
currentDir = os.path.dirname(os.path.abspath(__file__))
repertoire_source = os.path.join(currentDir, r"../../")
sys.path.append(repertoire_source)
import config as cf
import time as t

class TkinterDisplayer:

    def __init__(self, windowSize = [800, 410]):
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
        self.lightsPositions = [[70 * (i//cf.number_of_columns), 70 * (i%cf.number_of_columns)] for i in range(self.nbLights)] 
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

    def set_light_colors(self, colorList):
        if (not(self.windowClosed)):
            for i in range(self.nbLights):
                lightPos = self.lightIdToPos[self.nbLights-i-1]
                self.lights[lightPos][1] = colorList[i*4+1]
                self.lights[lightPos][2] = colorList[i*4+2]
                self.lights[lightPos][0] = colorList[i*4]
                self.lights[lightPos][3] = colorList[i*4+3]

    
    def update(self):
        if (not(self.windowClosed)):
            for i in range(self.nbLights):
                color = self.rgbw_to_rgb(self.lights[i])
                rct = self.rectangles[i]
                self.canvas.itemconfig(rct, fill=color)
            self.window.update()

            
        
    
    def rgbw_to_rgb(self, rgbw):
        convertedRed = max(0, rgbw[0] - rgbw[3])
        convertedGreen = max(0, rgbw[1] - rgbw[3])
        convertedBlue = max(0, rgbw[2] - rgbw[3])
        hexColor = "#{:02X}{:02X}{:02X}".format(int(convertedRed), int(convertedGreen), int(convertedBlue))

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
        


