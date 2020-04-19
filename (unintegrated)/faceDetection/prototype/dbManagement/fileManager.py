import os, cv2

class fileManager:
    """database manager for file structure database"""

    def __init__(self, path):
        self.db = path
        self.sizeOfDB = len(os.listdir(path))

    def insertIntoDB(self, label, image):
        """inserts entry into the database"""
        cv2.imwrite( self.getFullPath(label), image )
        self.sizeOfDB += 1

    def deleteFromDB(self, label):
        """deletes entry by label from the database"""
        os.remove( self.getFullPath(label) )
        self.sizeOfDB -= 1

    def updateInDB(self, label, image):
        """updates entry by label from the database"""
        self.deleteFromDB( label )
        self.insertIntoDB( label, image )

    def getFullPath(self, label):
        """gets the full path used to access an image from the database"""
        return self.db + '/' + label + ".jpg"

    def getSizeOfDB(self):
        """returns the number of entries in the database"""
        return self.sizeOfDB
