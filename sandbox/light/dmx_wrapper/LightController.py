import threading
import yaml
from queue import Queue

class LightController:
    def __init__(self, file_name=None):
        self.file_name = None
        self.num_lights = 0
        self.thread_list = []
        self.thread_queues = []

        if file_name:
            self.set_file(file_name)

    def _init_all_threads(self, data):
        for light_id in range(self.num_lights):
            self._init_thread(light_id, data)

    def _init_thread(self, light_id, data):
        thread = threading.Thread(target=self._worker, args=(light_id,data))
        thread.start()

        self.thread_list.append(thread)

    def set_file(self, file_name):
        data = self._read_yaml(file_name)

        if not isinstance(data, list):
            raise ValueError("Invalid YAML format. Expected a list.")

        for item in data:
            self._validate_yaml_item(item)

        self.quit()

        self.num_lights = len(data)
        self.file_name = file_name

        self._init_all_threads(data)


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
        print(f"Thread {light_id} started")
        thread_queue = Queue(maxsize=1)
        self.thread_queues.append(thread_queue)

        for light, id_chunk in enumerate(data):
            if light == light_id:
                for item in id_chunk.get('times', []):
                    thread_queue.put(item, block=True)
                    print(f"Thread {light_id} added block {item} to queue")


    def get_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            return self.thread_queues[light_id].queue[0]

    def get_next_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            return self.thread_queues[light_id].queue[1]

    def remove_block(self, light_id):
        if 0 <= light_id < self.num_lights:
            self.thread_queues[light_id].get()

    def empty_queues(self):
        for thread_queue in self.thread_queues:
            while not thread_queue.empty():
                thread_queue.get()

    def is_active(self):
        for thread in self.thread_list:
            if thread.is_alive():
                return True
        return False

    def quit(self):
        #self.empty_queues()
        for thread in self.thread_list:
            thread.join()

# # Example usage:
# controller = LightController('sandbox/light/yamls/test.yaml')
# print(controller.num_lights)
# print(controller.file_name)
# print(controller.get_block(2))
# print(controller.get_next_block(2))
# controller.remove_block(2)

# controller.quit()
