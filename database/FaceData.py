class FaceData:
    """Class to hold image and time it was processed for to pass throughout models"""
    def __init__(self, data, time=None):
        self._data = data
        if time is not None:
            self._time = time

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_time(self):
        return self._time
