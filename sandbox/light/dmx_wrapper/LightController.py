import threading
import yaml
from queue import Queue

class LightController:
    def __init__(self, nbLights):
        self.file_name = None
        self.num_lights = nbLights
        self.thread_list = {}
        self.thread_is_ready = {}
        self.thread_is_finished = {}
        self.thread_queues = {}

        #if file_name:
        #    self.set_file(file_name)

    def _init_all_threads(self, data):
        for light_id in range(self.num_lights):
            self._init_thread(light_id, data)
        while(len(self.thread_is_ready) != self.num_lights):
            continue
        while(False in [self.thread_is_ready[key] for key in self.thread_is_ready.keys()]):
            continue

    def _init_thread(self, light_id, data):
        thread = threading.Thread(target=self._worker, args=(light_id,data))
        thread.start()

        self.thread_list[str(light_id)] = thread

    def set_file(self, file_name):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")

        for item in data:
            self._validate_yaml_item(item)

        #self.num_lights = len(data)
        self.file_name = file_name

        self._init_all_threads(data)
        #self.quit()


    def _read_yaml(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = yaml.safe_load(file)
                return data
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise ValueError(f"Error reading YAML file: {e}")

    def _validate_yaml_item(self, item):
        for time_item in item.get('times', []):
            if 'dt' not in time_item or not isinstance(time_item['dt'], (int, float)) or time_item['dt'] < 25:
                raise ValueError("Invalid YAML format. 'dt' must be a positive number greater than or equal to 25.")
    
    def _worker(self, light_id, data):
        self.thread_is_ready[str(light_id)] = False
        self.thread_is_finished[str(light_id)] = False
        print(f"Thread {light_id} started")
        thread_queue = Queue(maxsize=10)
        self.thread_queues[str(light_id)] = thread_queue

        for light, id_chunk in enumerate(data):
            if id_chunk['id'] == light_id:
                for item in id_chunk.get('times', []):
                    thread_queue.put(item, block=True)
                    print(f"Thread {light_id} added block {item} to queue")
                    self.thread_is_ready[str(light_id)] = True
        self.thread_is_ready[str(light_id)] = True
        self.thread_is_finished[str(light_id)] = True


    def get_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            if (self.thread_queues[str(light_id)].qsize() > 0):     
                return self.thread_queues[str(light_id)].queue[0]
            elif self.thread_is_finished[str(light_id)]:
                return {'dt': -1, 'red': 255, 'green': 255, 'blue': 255, 'white': 200, 'Tr': 0}
            else:
                while(self.thread_queues[str(light_id)].qsize() == 0):
                    continue
                return self.get_block(light_id)
        else:
            raise Exception(f"Wrong light id in get_block. Given id : {light_id}")

    def get_next_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            if (self.thread_queues[str(light_id)].qsize() > 1): 
                return self.thread_queues[str(light_id)].queue[1]
            else:
                return {'dt': -1, 'red': 255, 'green': 255, 'blue': 255, 'white': 200, 'Tr': 0}

    def remove_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            self.thread_queues[str(light_id)].get()

    def empty_queues(self):
        for thread_queue in self.thread_queues:
            while not thread_queue.empty():
                thread_queue.get()

    def is_active(self):
        for lightId in range(self.num_lights):
            if self.thread_list[str(lightId)].is_alive() or self.thread_queues[str(lightId)].qsize() != 0:
                return True
            #print(lightId, self.thread_queues[str(lightId)].qsize())
            
        return False

    def quit(self):
        #self.empty_queues()
        for lightId in range(self.num_lights):
            self.thread_list[str(lightId)].join()

# # Example usage:
# controller = LightController('sandbox/light/yamls/test.yaml')
# print(controller.num_lights)
# print(controller.file_name)
# print(controller.get_block(2))
# print(controller.get_next_block(2))
# controller.remove_block(2)

# controller.quit()
