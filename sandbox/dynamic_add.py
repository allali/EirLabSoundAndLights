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
import config as cf

from New_player import YamlReader, Player

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
yr.load_file(r"./light/yamls/test.yaml", player)
#yr.load_file(r"./light/yamls/test.yaml", player, 1000)
player.start()

current_light = {'x':None, 'y':None}

while True:
    key = detect_keypress()
    print(f"Touche pressée : {key}")

    if key == 'z' and current_light['x'] is not None and current_light['y'] < cf.number_of_columns -1:
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [200,200,200,200], 0, 0)
        current_light['y'] += 1 
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [255,0,0,0], 0, 0)

    if key == 'q' and current_light['x'] is not None and current_light['x'] < cf.number_of_rows -1:
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [200,200,200,200], 0, 0)
        current_light['x'] += 1
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [255,0,0,0], 0, 0)

    if key == 's' and current_light['x'] is not None and current_light['y'] > 0:
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [200,200,200,200], 0, 0)
        current_light['y'] -= 1
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [255,0,0,0], 0, 0)

    if key == 'd' and current_light['x'] is not None and current_light['x'] > 0:
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [200,200,200,200], 0, 0)
        current_light['x'] -= 1
        player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [255,0,0,0], 0, 0)

    if key == 'r':
        if current_light['x'] is not None:
            player.add(current_light['x'] * cf.number_of_columns + current_light['y'], player.timer.get_time() + 540, [200,200,200,200], 0, 0)

        point = random.randint(0,53)
        current_light['x'] = int(point / cf.number_of_columns)
        current_light['y'] = int(point % cf.number_of_columns)
        player.add(point, player.timer.get_time() + 540, [255,0,0,0], 0, 0)

    if key == 'p':
        break

player.quit()