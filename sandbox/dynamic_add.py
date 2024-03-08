import sys
import tty
import time
import random
import termios
import keyboard
import tkinter as tk
sys.path.append("./light/dmx_wrapper")
sys.path.append("./light")
sys.path.append("./sound")
import bindings

from Player import YamlReader, Player

def detect_keypress():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        key = sys.stdin.read(1)
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


nbLights = 54
interfaceName = "FT232R" # "FT232R" "TkinterDisplayer"
player = Player(54, interfaceName)
yr = YamlReader()
yr.load_file(r"./light/yamls/test.yaml", player, 0, False)
#yr.load_file(r"./light/yamls/test.yaml", player, 1000)
player.start()

while True:
    key = detect_keypress()
    print(f"Touche pressée : {key}")

    if key == 'q':
        break

    if key == 'r':
        player.add_new_set()
        player.add(random.randint(0,53), 500, [255,0,0,0], 0, 200, True)

    player.quit()