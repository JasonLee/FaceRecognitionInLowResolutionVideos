# -*- coding: utf-8 -*-
"""This module defines the database which is used by face recognition system.
"""
import os
import io
from database.database import *
import numpy as np   
from PIL import Image

class Database:
    """This class defines the database which is used by face recognition system.
    The database should be organised as: root directory -> (folders with identity name) -> (images for the same person in same folder)
    
    Args:
        path (str): path of the database root directory
    """
    def __init__(self, path):
        self.__dbpath = path

    def getNames(self):
        """Get all names stored in this database
        Returns:
            a list of names.
        """
        return get_all_people_names()

    def getImages(self, name):
        """Get images of a specific person

        Args:
            name (str): name of the identity.

        Returns:
            an iterator which contains all images of the identity
        """
        if(name in get_all_people_names()):

            class images:
                def __init__(self, name):
                    self.list = get_people_image(name)

                    for i in range(len(self.list)):
                        img = Image.open(io.BytesIO(self.list[i]))
                        self.list[i]= np.asarray(img)

                    self.list = iter(self.list)

                def __iter__(self):
                    return self

                def __next__(self):
                    return next(self.list)

            return images(name)
        else:
            return -1

    def getSize(self):
        """Get number of identities in the database

        Returns:
            int: size of the database
        """
        return len(get_all_people_names())

    def saveImage(self, identity, face_name, face):
        """Save the image of an identity to database

        Args:
            identity (str): the name of identity
            face_name (str): name of the file to save as.
            face : the face to be saved.
        """
        if identity not in get_all_people_names():
            insert_people(identity)

        face.save(self.__dbpath+'/'+identity+'/'+face_name+'.png')
