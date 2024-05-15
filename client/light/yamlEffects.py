from light.yaml_manager import YamlWritter
from light_configuration import LIGHTS_COORDINATES
import numpy as np
from typing import List

    

def dist(P1, P2):
    return np.sqrt(np.sum((P2-P1)**2))


def light_yaml_from_ring(center:np.ndarray, radius:int, t0:int, rgbw:List[int], lightId, ym:YamlWritter):
    if radius == 0:
        return
    d = dist(center, LIGHTS_COORDINATES[lightId])
    if d > radius:
        return
    ratio = (d / radius)**2


        
    color = rgbw * ratio
    ym.add(lightId, t0, color[0], color[1], color[2], color[3], 1)
    


def light_yaml_from_circle(center:np.ndarray, radius:int, t0:int, rgbw:List[int], lightId, ym:YamlWritter):
    if radius == 0:
        return
    d = dist(center, LIGHTS_COORDINATES[lightId])
    if d > radius:
        return
    if d!=0:
        ratio = 1 - (d / radius)
    else: 
        ratio = 1
        
    color = rgbw * ratio
    ym.add(lightId, t0, color[0], color[1], color[2], color[3], 1)
                

def light_yaml_from_rectangle(center:np.ndarray, dimensions:List[int], t0:int, rgbw:List[int], lightId, ym:YamlWritter):
    dh = abs(center[0] - LIGHTS_COORDINATES[lightId][0])
    dl = abs(center[1] - LIGHTS_COORDINATES[lightId][1])
    

    if (dh < dimensions[0] and dl < dimensions[1]):
        ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], 1)
    
    

            
            
            
class YamlEffectWritter:
        
    @staticmethod
    def rectangle_appear(start:np.ndarray, stop:np.ndarray, dimensions:int, t0:int, t1:int, rgbw:List[int], ym:YamlWritter, precision=200):
        timeInterval = precision
        times = np.arange(t0, t1, timeInterval)
        totalIterations = len(times) 
        for i, ti in enumerate(times[:-1]):
            for lightId in range(54):
                light_yaml_from_rectangle(start + i*(stop-start)/totalIterations, dimensions, ti, rgbw.astype(np.uint8), lightId, ym)
        for lightId in range(54):
            light_yaml_from_rectangle(stop, dimensions, t1, rgbw, lightId, ym)

        
    @staticmethod
    def ring_appear(center:np.ndarray, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:YamlWritter):
        timeInterval = 45
        times = np.arange(t0, t1, timeInterval)
        totalIterations = len(times) 
        for i, ti in enumerate(times[:-1]):
            for lightId in range(54):
                light_yaml_from_ring(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
        for lightId in range(54):
            light_yaml_from_ring(center, finalRadius, t1, rgbw, lightId, ym)
            
    @staticmethod
    def circle_appear(center:np.ndarray, finalRadius:int, t0:int, t1:int, rgbw:List[int], ym:YamlWritter):
        timeInterval = 150
        times = np.arange(t0, t1, timeInterval)
        totalIterations = len(times) 
        for i, ti in enumerate(times):
            for lightId in range(54):
                light_yaml_from_circle(center, finalRadius * i / totalIterations, ti, rgbw.astype(np.uint8), lightId, ym)
        for lightId in range(54):
            light_yaml_from_circle(center, finalRadius, t1, rgbw, lightId, ym)
            
            
    @staticmethod
    def set_color(ym:YamlWritter, rgbw:List[int], t0:int, Tr:int=0):
        for lightId in range(54):
            ym.add(lightId, t0, rgbw[0], rgbw[1], rgbw[2], rgbw[3], Tr)