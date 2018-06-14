

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 15:54:53 2018

@author: brain
 
This function displays a video from the Grasshopper cameras WITHOUT GRABBING ANYTHING
"""
import PyCapture2 as py2
import cv2
import numpy as np

#import time


bus = py2.BusManager()
numCams = bus.getNumOfCameras()
print "Number of cameras detected: ", numCams
if not numCams:
	print "Insufficient number of cameras. Exiting..."
	exit()

# Select camera on 0th index
c = py2.Camera()
uid = bus.getCameraFromIndex(0)
c.connect(uid)

fmt7info, supported = c.getFormat7Info(0)
fmt7imgSet = py2.Format7ImageSettings(0, 0, 0, 2048, 1536, py2.PIXEL_FORMAT.MONO8)
fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)
if not isValid:
	print "Format7 settings are not valid!"
	exit()
 
c.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)

print "Starting image capture..."

c.startCapture()

while(True):

             image = c.retrieveBuffer()
             
#             a_bgr = np.array(image)
             
             image = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) );
             
#             a_rgb = cv2.cvtColor(a_bgr, cv2.COLOR_RGB2GRAY)
             
             cv2.imshow('image', image) 
             
             if cv2.waitKey(30) & 0xFF == ord('q'):
                 break
c.stopCapture()


# Disable camera embedded timestamp

c.disconnect()
cv2.destroyAllWindows()
    