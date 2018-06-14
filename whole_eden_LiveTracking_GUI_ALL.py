# -*- coding: utf-8 -*-
"""
Created on Sat May 26 12:18:05 2018

@author: brain
"""
import PyCapture2
import cv2
import numpy as np
import time
from sys import exit


def printBuildInfo():
	libVer = PyCapture2.getLibraryVersion()
	print "PyCapture2 library version: ", libVer[0], libVer[1], libVer[2], libVer[3]
	print

def printCameraInfo(cam):
	camInfo = cam.getCameraInfo()
	print "\n*** CAMERA INFORMATION ***\n"
	print "Serial number - ", camInfo.serialNumber
	print "Camera model - ", camInfo.modelName
	print "Camera vendor - ", camInfo.vendorName
	print "Sensor - ", camInfo.sensorInfo
	print "Resolution - ", camInfo.sensorResolution
	print "Firmware version - ", camInfo.firmwareVersion
	print "Firmware build time - ", camInfo.firmwareBuildTime

# Print PyCapture2 Library Information
printBuildInfo()

# Ensure sufficient cameras are found
bus = PyCapture2.BusManager()
numCams = bus.getNumOfCameras()
print "Number of cameras detected: ", numCams
if not numCams:
	print "Insufficient number of cameras. Exiting..."
	exit()

# Select camera on 0th index
c = PyCapture2.Camera()
uid = bus.getCameraFromIndex(0)
c.connect(uid)
printCameraInfo(c)

fmt7info, supported = c.getFormat7Info(0)

fmt7imgSet = PyCapture2.Format7ImageSettings(0, 700, 400, 1040, 1000, PyCapture2.PIXEL_FORMAT.MONO8)


fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)

if not isValid:
	print "Format7 settings are not valid!"
	exit()
 
c.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)

print "Starting image capture..."

c.startCapture()

image = c.retrieveBuffer()
              
image = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) );
 
a_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

a_bgr = cv2.medianBlur(a_bgr,5)


while(True):
    
    cv2.imshow("First Frame", image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        
        break
    
cv2.destroyWindow("First Frame")

# Disable camera embedded timestamp

tracker = cv2.TrackerBoosting_create()

# Uncomment the lines below to select a different bounding box

cv2.namedWindow("roi", cv2.WINDOW_NORMAL)

cv2.resizeWindow("roi", 800,800)

bbox = cv2.selectROI( "roi", a_bgr, False, False)

# Tracking initialization passing the 1st frame and the selected ROI

ok = tracker.init(a_bgr, bbox)

cv2.destroyWindow("roi")

tip = [(0,0)]


while True:

        image = c.retrieveBuffer()
             
#             a_bgr = np.array(image)
             
        image = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) );
        
        a_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        a_bgr = cv2.medianBlur(a_bgr,5) 

                
        if not ok:
            
            break
        
        # Update tracker passing the new frame. Output: new Bounding Box
    
        ok, bbox = tracker.update(a_bgr)
        
        if ok:
            
            # Tracking success
            
            # pass to grayscale

            gr = cv2.cvtColor(a_bgr, cv2.COLOR_BGR2GRAY)
            
            #Thresholding the grayscale image in a BINARY image: 0 or 255
            
            retval, th = cv2.threshold(gr, 30, 255, cv2.THRESH_BINARY)
            
            # Saving the borders of the ROI
            
            n_o = [int(bbox[0]),int(bbox[1])]
            
            print "Upper Left is: " , n_o
            
#            cv2.circle(th, (int(bbox[0]),int(bbox[1])) , 5, (0,0,0), -1)
            
            n_e = [int(bbox[0]+ bbox[2]),int(bbox[1])]
            
            print "Upper Right is: " , n_e

#            cv2.circle(th, (int(bbox[0]+ bbox[2]),int(bbox[1])) , 5, (0,0,0), -1)
            
            s_o = [int(bbox[0]),int(bbox[1]+ bbox[3])]
            
            print "Lower Left is: " , s_o
 
#            cv2.circle(th, (int(bbox[0]),int(bbox[1]+ bbox[3])) , 5, (0,0,0), -1)
            
            s_e = [int(bbox[0]+ bbox[2]),int(bbox[1]+bbox[3])]
            
            print "Lower Right is: " , s_e

#            cv2.circle(th, (int(bbox[0]+ bbox[2]),int(bbox[1]+bbox[3])) , 5, (0,0,0), -1)
            
            print "=================="
            
            # Mark the updated ROI with a Rectangle
            
            cv2.rectangle(image, tuple(n_o), tuple(s_e), (255,255,0), 1, 1)  
            
            cv2.rectangle(th, tuple(n_o), tuple(s_e), (0,0,0), 1, 1)  
            
            it=0
            
            pmax=(0,0)
            
            # Scanning every pixel of the moving ROI 
            
            for i in range (n_o[0]+5,n_e[0]-5):
                
                for j in range(n_o[1]+5,s_o[1]-5):
                    
                    # check the value of the pixel
                    
                    if th[j][i]==0 :
                        
                        # If the pixel is black, it is part of the Needle
                        
                        # Saving its coordinates
                        
                        p=(i,j)
                        
                        #the maximum of the black pixel is the tip
                        
                        if p[1] > pmax[1]  and it<1:
                                                        
                            pmax = p
                            
                            # Ouput: tip 2D-coordinates
                                
                            print ' x of the tip is: ', pmax[0], '   and y of the tip is: ', pmax[1]

                            cv2.circle(gr, tuple(pmax) , 10, (0,0,0), -1)
                            
                            cv2.circle(th, tuple(pmax) , 10, (0,0,0), -1)
                            
                            it = it + 1 
                            
                            tip.append(pmax)
                            
                                                
        # Display results to have a visual feedback
        
        cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
        
        cv2.resizeWindow("Tracking", 800,800)
        
        cv2.imshow("Tracking", gr)    # grayscale image
        
        cv2.namedWindow("Th", cv2.WINDOW_NORMAL)

        cv2.resizeWindow("Th", 800,800)

        cv2.imshow("Th", th) # binary image
        
        
        if cv2.waitKey(20) & 0xFF == ord('q'):
            
            break
        
c.stopCapture()

c.disconnect()

cv2.destroyAllWindows()

# Save tip coordinates in a text file for future uses

np.savetxt('tipinROI_camera1.txt', tip)   
