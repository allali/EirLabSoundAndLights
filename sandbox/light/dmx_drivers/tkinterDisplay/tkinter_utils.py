import os
import sys
import bindings
import time

try:
    currentDir = os.path.dirname(os.path.abspath(__file__))
    repertoire_source = os.path.join(currentDir, r"../../")
    sys.path.append(repertoire_source)
    import config as cf
except:
    raise Exception("Path to config.py not found")

import tkinter as tk


bgColor = "#555555"

class TkinterDisplayer:

    startTime = 0

    def __init__(self, windowSize = [727, 455]):
        """
        Initialize and launch the displayer
        """
        self.nbLights = 54
        self.exitProgram = False
        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.destroy_displayer)
        self.window.bind('<Escape>', self.destroy_displayer)
        self.window.bind('<Control-C>', self.destroy_displayer) 
        self.window.bind('<Control-c>', self.destroy_displayer)
        self.extern_bindings()
        self.windowClosed = False
        self.window.title("DMX Lights Displayer")
        self.window.geometry(f"{windowSize[0]}x{windowSize[1]}")
        self.window.configure(bg=bgColor)
        self.canvas = tk.Canvas(self.window, width=windowSize[0], height=windowSize[1], bg=bgColor,highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.lights = [[0,0,0,0] for i in range(self.nbLights)]
        self.lightsPositions = [[50 + 70 * (i//cf.number_of_columns), 70 * (i%cf.number_of_columns) + 20] for i in range(self.nbLights)] 
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
        self.timeLabel = tk.Label(self.canvas, text="Time : 0 ms", bg=bgColor, foreground="#FFFFFF")
        self.timeLabel.place(x=0, y=0, anchor="nw")
        

    def set_light_colors(self, colorList):
        """
        Update the instance with the new color datas received
        """
        if (not(self.windowClosed)):
            for i in range(self.nbLights):
                lightPos = self.lightIdToPos[self.nbLights-i-1]
                self.lights[lightPos][1] = colorList[i*4+1]
                self.lights[lightPos][2] = colorList[i*4+2]
                self.lights[lightPos][0] = colorList[i*4]
                self.lights[lightPos][3] = colorList[i*4+3]

    def draw_lights(self):
        """
        Changes the color of the light representations
        """
        for i in range(self.nbLights):
            color = self.rgbw_to_rgb(self.lights[i])
            rct = self.rectangles[i]
            self.canvas.itemconfig(rct, fill=color)
    
    def draw_light_ids(self):
        """
        Display the lights ids below their rectangular representations
        """
        ypad = 46
        for i in range(self.nbLights):
            xpad = (18 if (self.nbLights-i-1 > 9) else 22)
            x= self.lightsPositions[i][0] + xpad
            y= self.lightsPositions[i][1] + ypad
            label = tk.Label(self.canvas, text=str(self.nbLights-i-1), bg=bgColor, foreground="#FFFFFF")
            label.place(x=x, y=y, anchor="nw")
    
    def draw_timer(self):
        if (self.startTime != 0):
            t = str(round((time.time() - self.startTime) * 1000))
            timeText = "Time : " + (t[:len(t)-3] + " " + t[len(t)-3:] if len(t) > 3 else t) + " ms"
            self.timeLabel.config(text=timeText)

    
    def update(self):
        """
        Update the display
        """
        if (not(self.windowClosed)):
            self.draw_lights()
            self.draw_timer()
            self.window.update()
        if (self.startTime == 0):
            self.startTime = time.time()


        
    
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
        """
        Close the displayer. This function is called by the upper functions.
        """
        if not(self.windowClosed):
            self.destroy_displayer()

    def destroy_displayer(self, event=None):
        """
        Close the displayer. This function will be called when closing manually the display.
        The window can be closed using ESC or CTRL^C. Using CTRL^C will also stop main process.
        """
        self.window.destroy()
        self.windowClosed = True
        if (event is not None and event.keycode == 54): # ctrl^C should notify the main thread to stop the process
            self.exitProgram = True
            

    def extern_bindings(self):
        self.window.bind('<z>', lambda event: bindings.move('z'))
        self.window.bind('<q>', lambda event: bindings.move('q'))
        self.window.bind('<s>', lambda event: bindings.move('s'))
        self.window.bind('<d>', lambda event: bindings.move('d'))
