import os
from skimage import io
from torchvision.utils import save_image

"""The database should be managed as (folder)->(folders named by people)->(images)"""
class Database:
    """database manager for file structure database"""

    def __init__(self, path):
        self.dbpath = path
        self.entry = os.listdir(path)           #People's name

    def getNames(self):
        """Get all names stored in this database"""
        return self.entry

    def getImages(self, name):
        """Get images of a specific person"""
        if(name in self.entry):
            class images:
                def __init__(self, name, path):
                    self.path = path +"/"+name
                    self.list = iter(os.listdir(self.path))
                def __iter__(self):
                    return self
                def __next__(self):
                    return io.imread(self.path+"/"+next(self.list))
            return images(name, self.dbpath)
        else:
            return -1
    def getSizeOfDB(self):
        """returns the number of entries in the database"""
        size = {}
        for i in self.entry:
            size[i] = len(os.listdir(self.dbpath +"/"+i))
        return size

    def saveImage(self, person_name, face_name, face):
        save_image(face, self.dbpath+'/'+name+'/'+face_name+'.png')
