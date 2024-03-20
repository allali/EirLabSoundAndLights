import numpy as np
import yaml

class yaml_writting_utils:
    
    def __init__(self, coordinatesFile, yamlManager):
        self.lights, self.speakers = yaml_writting_utils.load_file(coordinatesFile)
        self.nbLights = len(self.lights)
        self.nbSpeakers = len(self.speakers)
        self.ym = yamlManager
    
    
    
    def read_yaml(file_name):
        """
        Opens and reads a yaml file
        """
        try:
            with open(file_name, 'r') as file:
                
                data = yaml.safe_load(file)
                return data
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise ValueError(f"Error reading YAML file: {e}")
            
    def load_file(file_name):
        """
        Loads the yaml file containing informations about the positions of the speakers and the lights.
        """
        data = yaml_writting_utils.read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")
        
        lights = []
        speakers = []
        lights_data = data[0]["lights"]
        speakers_data = data[1]["speakers"]
        
        for lightId, light in enumerate(lights_data):
            if lightId != light["id"]:
                ValueError(f"Exepected id {lightId}, got { light['id'] }")
            lights.append([light["x"], light["y"], light["z"]])
            
        for speakerId, speaker in enumerate(speakers_data):
            if speakerId != speaker["id"]:
                ValueError(f"Exepected id {speakerId}, got { speaker['id'] }")
            speakers.append([speaker["x"], speaker["y"], speaker["z"]])
        
        return (np.array(lights), np.array(speakers))



    def static_glow(self, position, offset:int, duration:int, func=lambda x:(x**5)):
        """
        Add to the yaml file a static glow at a given position, the radius of the glow depends on the func given. The glows starts at offset, and finish at offet+duration
        """
        dataSet = np.zeros((self.nbLights), dtype=np.float64)
        for lightId, light in enumerate(self.lights):
            dataSet[lightId] = self.dist(position, light)
        dataSet = np.sqrt(dataSet)
        
        dataSet = 1 - self.normalize_data_set(dataSet)
        dataSet = func(dataSet)
        colorMap = self.distance_map_to_rgbw(dataSet)
        for lightId, color in enumerate(colorMap):
            self.ym.add(lightId, offset, color[0], color[1], color[2], color[3], 0)
            self.ym.add(lightId, offset+duration, color[0], color[1], color[2], color[3], 0)
    
    def distance_map_to_rgbw(self, dataSet, dist_to_rgbw_func = lambda x,dim: x*255):
        """
        Transform a map of distances into a numpy array of colors. 
        Args:
            - dataSet : a unidimensional numpy array to transform
            - dist_to_rgbw_func : a numpy friendly function. This functions must take 2 arguments dist_to_rgbw_func(distanceMap, dimension).
                You need to expect your numpy array dataSet in first argument. The second argument is an integer between 0 and 3 that indicates wether you're computing red (0), green (1), blue (2) or white (3).
                This function must return a numpy array of shape (dataSet.size).
                
        Returns a numpy array of shape (distanceMap.size, 4). Values inside this array are of type np.uint8
        """
        colorMap = np.zeros((dataSet.size, 4), dtype=np.uint8)
        colorMap[:, 0] = dist_to_rgbw_func(dataSet, 0)
        colorMap[:, 1] = dist_to_rgbw_func(dataSet, 1)
        colorMap[:, 2] = dist_to_rgbw_func(dataSet, 2)
        colorMap[:, 3] = dist_to_rgbw_func(dataSet, 3)
        return colorMap
    
    def get_line_step(self, Pi, Pf, ratio:float):
        if (ratio > 1 or ratio < 0):
            raise ValueError(f"Expected ratio between 0 and 1, got f{ratio}")
        if len(Pi) != len(Pf):
            raise ValueError("initial and final dimensions are different")
        currentPos = Pi + (Pf-Pi)*ratio 
        distanceTable = np.zeros((self.nbLights), dtype=np.float64)
        for lightId, light in enumerate(self.lights):
            distanceTable[lightId] = self.dist(currentPos, light)
        distanceTable = np.sqrt(distanceTable)
        return distanceTable
    
    def moving_glow(self ,startPosition, endPosition, offset:int, duration:int, func=lambda x:(x**5)):
        for i in range(min(10, int(duration//27 - 1))):
            dataSet = self.get_line_step(startPosition, endPosition, i/(duration//27))
            dataSet = 1 - self.normalize_data_set(dataSet)
            dataSet = func(dataSet)
            colorMap = self.distance_map_to_rgbw(dataSet)
            for lightId, color in enumerate(colorMap):
                self.ym.add(lightId, offset+ i*27, color[0], color[1], color[2], color[3], 1)
        
        dataSet = self.get_line_step(startPosition, endPosition, 1)
        dataSet = 1 - self.normalize_data_set(dataSet)
        dataSet = func(dataSet)
        colorMap = self.distance_map_to_rgbw(dataSet)
        for lightId, color in enumerate(colorMap):
            self.ym.add(lightId, offset+ duration, color[0], color[1], color[2], color[3], 1)
                
    def normalize_data_set(self, dataSet):
        """
        Normalize values from dataSet between 0 and 1
        """
        dataSet -= np.min(dataSet)
        return dataSet/np.max(dataSet)
    
    
    def dist(self, P1, P2):
        """
        Returns the square of the distance between P1 and P2. P1 and P2 can be multi-dimensional numpy arrays
        """
        return np.sum((P2-P1)**2)
