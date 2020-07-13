import queue
import threading


class SharedData:
    """Contains all queues and threading for super resolution and face recognition"""

    def __init__(self, controller):
        self.controller = controller
        if self.controller.get_settings().value("Toggle SR", 1, int) == 1:
            self.ganQueueCount = threading.Semaphore(0)
            self.ganQueue = queue.Queue()
            self.ganDone = threading.Event()

        self.recogQueueCount = threading.Semaphore(0)
        self.recogQueue = queue.Queue()
        self.detDone = threading.Event()

    def reset(self):
        """Resets the super resolution and face recognition queues; clears the detection done and super resolution
        done flags. """
        if self.controller.get_settings().value("Toggle SR", 1, int) == 1:
            self.ganQueue.queue.clear()
            self.ganDone.clear()
        self.recogQueue.queue.clear()
        self.detDone.clear()
