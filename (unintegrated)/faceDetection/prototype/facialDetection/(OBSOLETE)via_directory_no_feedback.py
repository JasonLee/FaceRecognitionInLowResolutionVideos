# import cv2
# from facialDetection.facialDetectionManager import facialDetectionManager
#
# class directoryFDM(facialDetectionManager):
#     """performs facial detection on images in a directory"""
#
#     def run(self):
#         """reads frames from the celebs_in directory"""
#         for i in range(1, 202599):
#             self.setFrame( cv2.imread("input/{:06d}.jpg".format(i)) )
#             self.locateFaces()
#             self.storeFaces( "output", "{:06d}".format(i) )
#
# directoryFDM()