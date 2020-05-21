class FaceData:
    def __init__(self, data, time = None):
        self.__data = data
        if time is not None:
            self.__time = time


    def get_data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    def get_time(self):
        return self.__time


