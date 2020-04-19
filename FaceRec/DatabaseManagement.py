# -*- coding: utf-8 -*-
"""This module defines the database which is used by face recognition system.
"""
import os
from skimage import io

class Database:
    """This class defines the database which is used by face recognition system.
    The database should be organised as: root directory -> (folders with identity name) -> (images for the same person in same folder)
    
    Args:
        path (str): path of the database root directory
    """
    def __init__(self, path):
        self.__dbpath = path
        self.__entry = os.listdir(path)           #People's name

    def getNames(self):
        """Get all names stored in this database
        Returns:
            a list of names.
        """
        return self.__entry

    def getImages(self, name):
        """Get images of a specific person

        Args:
            name (str): name of the identity.

        Returns:
            an iterator which contains all images of the identity
        """
        if(name in self.__entry):
            class images:
                def __init__(self, name, path):
                    self.path = path +"/"+name
                    self.list = iter(os.listdir(self.path))
                def __iter__(self):
                    return self
                def __next__(self):
                    return io.imread(self.path+"/"+next(self.list))
            return images(name, self.__dbpath)
        else:
            return -1
    def getSize(self):
        """Get number of identities in the database

        Returns:
            int: size of the database
        """
        size = {}
        for i in self.__entry:
            size[i] = len(os.listdir(self.__dbpath +"/"+i))
        return size

    def saveImage(self, identity, face_name, face):
        """Save the image of an identity to database

        Args:
            identity (str): the name of identity
            face_name (str): name of the file to save as.
            face : the face to be saved.
        """
        if identity not in self.__entry:
            os.mkdir(self.__dbpath+'/'+identity)
        face.save(self.__dbpath+'/'+identity+'/'+face_name+'.png')
