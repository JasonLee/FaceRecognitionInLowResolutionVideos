class Queue:
    """This class implements a Queue.

    Attributes:
        Head (Node): the head of the list.
        Tail (Node): the tail of the list.
    """

    def __init__(self):
        self.head = None
        self.tail = None

    def reset(self):
        """
        Reset head and tail to None, clean the queue.
        """
        self.head = None
        self.tail = None

    def empty(self):
        """
        Reture if the queue is empty.
        """
        if self.head == None:
            return 1
        else:
            return 0

    def push(self, data):
        """
        Push a piece of data to queue.
        """
        if self.empty():
            self.head = Node(data)
            self.tail = self.head
        else:
            node = Node(data)
            self.tail.next = node
            self.tail = node

    def pop(self):
        """
        Pop a piece of data from queue.

        Returns:
            the first data in queue if the queue isn't empty, None otherwise.
        """
        if self.empty():
            return None
        else:
            data = self.head.data
            self.head = self.head.next
            if self.empty():
                self.tail = None
            return data

class Node:
    """
    Single linked list of data.
    
    Args:
        data: data to store.
    
    Attributes:
        data: stored data.
        next (Node): next node in the list.
    """
    def __init__(self, data):
        self.data = data
        self.next = None