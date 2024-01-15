import dmx
import config as cf

lights = None
interface = None
universe = None

current_light = {'x':0, 'y':0}

def set_bindings(l, i, u):
    global lights, interface, universe
    lights = l
    interface = i
    universe = u

def move(move):
    if lights is not None and interface is not None and universe is not None:
        global current_light
        old = {'x':current_light['x'], 'y':current_light['y']}

        if move == 'z' and current_light['y'] < cf.number_of_columns -1:
            current_light['y'] += 1  

        if move == 'q' and current_light['x'] < cf.number_of_rows -1:
            current_light['x'] += 1

        if move == 's' and current_light['y'] > 0:
            current_light['y'] -= 1

        if move == 'd' and current_light['x'] > 0:
            current_light['x'] -= 1
        
        lights[old['x'] * cf.number_of_columns + old['y']]["light"].set_colour(dmx.Color(0,0,0))
        lights[current_light['x'] * cf.number_of_columns + current_light['y']]["light"].set_colour(dmx.Color(0,0,255))
        interface.set_frame(universe.serialise())
        interface.send_update()
