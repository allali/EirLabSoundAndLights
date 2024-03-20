import sys
import tty
import time
import random
import termios
import keyboard
import threading
import tkinter as tk
sys.path.append("./light/dmx_wrapper")
sys.path.append("./light")
sys.path.append("./sound")
import bindings

from New_player import YamlReader, Player

key = None
def detect_keypress():
    global key
    while True:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            key = sys.stdin.read(1)
            if key == 'q':
                break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


nbLights = 54
interfaceName = "FT232R" # "FT232R" "TkinterDisplayer"
player = Player(54, interfaceName)
yr = YamlReader()
yr.load_file(r"./light/yamls/test.yaml", player)
#yr.load_file(r"./light/yamls/test.yaml", player, 1000)
player.start()
time.sleep(2)

threading.Thread(target=detect_keypress).start()

snake = [8, 14, 20, 26]

while True:

    player.add((snake[0]-6)%54, player.timer.get_time() + 540, [200,200,200,200], 0, 0)

    for i in range(4):
        player.add(snake[i]%54, player.timer.get_time() + 540, [0,0,255,0], 0, 0)

    time.sleep(0.5)
    for i in range(4):
        snake[i] += 6

    if key == 'q':
        break

player.quit()