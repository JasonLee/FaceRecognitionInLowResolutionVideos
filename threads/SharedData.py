from threads.queue import Queue
import threading

class SharedData:
    """This class contains all the data structures which are shared between the face detection, super resolution and
    face recognition threads.

    Attributes:
        ganQueueCount: a semaphore denoting the number of faces in the super resolution queue.
        ganQueue: the super resolution queue.
        recogQueueCount: a semaphore denoting the number of faces in the face recognition queue.
        recogQueue: the face recognition queue.
        detDone: a flag to identify if detection has been run on an image or on every frame from a video source.
        ganDone: a flag to identify if super resolution has finished.
    """
    def __init__(self, controller):
        self.controller = controller
        if self.controller.get_settings().value("Toggle SR", 1, int) == 1:
            self.ganQueueCount = threading.Semaphore(0)
            self.ganQueue = Queue()
            self.ganDone = threading.Event()

        self.recogQueueCount = threading.Semaphore(0)
        self.recogQueue = Queue()
        self.detDone = threading.Event()


    def reset(self):
        """Resets the super resolution and face recognition queues; clears the detection done and super resolution done flags."""
        if self.controller.get_settings().value("Toggle SR", 1, int) == 1:
            self.ganQueue.reset()
            self.ganDone.clear()
        self.recogQueue.reset()
        self.detDone.clear()
