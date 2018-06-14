# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 18:23:19 2018

@author: brain
"""

import PyCapture2 as py2
import cv2

import numpy as np
from sys import exit

def printBuildInfo():
    
	libVer = py2.getLibraryVersion()
	print "PyCapture2 library version: ", libVer[0], libVer[1], libVer[2], libVer[3]
	

def printCameraInfo(c):
    
	camInfo = c.getCameraInfo()
 
	print "\n*** CAMERA INFORMATION ***\n"
	print "Serial number - ", camInfo.serialNumber
	print "Camera model - ", camInfo.modelName
	print "Camera vendor - ", camInfo.vendorName
	print "Sensor - ", camInfo.sensorInfo
	print "Resolution - ", camInfo.sensorResolution
	print "Firmware version - ", camInfo.firmwareVersion
	print "Firmware build time - ", camInfo.firmwareBuildTime


def connectpyCapture(camera_):
    
    printBuildInfo()
    
    bus = py2.BusManager()
    
    numCams = bus.getNumOfCameras()
        
    print "Number of cameras detected: ", numCams
    
    if not numCams:
        
        	print "Insufficient number of cameras. Exiting..."
         
        	exit()

    c = py2.Camera()
    py2.Config.highPerformanceRetrieveBuffer = True
        
    c.connect(bus.getCameraFromIndex(camera_))
    
    
    printCameraInfo(c)
    
    
    
#    fmt7info, supported = c.getFormat7Info(0)
    
#    print "Connecting to  camera: " , bool
            
    c.getFormat7Configuration()
    
    if camera_ == 0:
    
        fmt7imgSet = py2.Format7ImageSettings(0, 0, 0, 2048, 900, py2.PIXEL_FORMAT.MONO8)
    
    else:
        
        fmt7imgSet = py2.Format7ImageSettings(0, 700, 400, 1040, 1000, py2.PIXEL_FORMAT.MONO8)
    
    fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)
    
    c.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)
    
    c.startCapture()

    return c
        
def readpyFrame(c):
    
    # image IS THE RAW IMAGE IN MONO8
    
        
    image = c.retrieveBuffer()
    
#    print  " pixel format  " , image.getPixelFormat()
    
#    print " data stream" , image.getData()
    
#    print max(image.getData())
    
#    print min(image.getData())
            
    gr = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) )
 
    a_bgr = cv2.cvtColor(gr, cv2.COLOR_GRAY2BGR)
   
    a_bgr = cv2.medianBlur(a_bgr,5)
    
    gr = cv2.medianBlur(gr,5)

    return a_bgr, gr

    
def circlesROI_AUTO(gr):
        
    retval, th = cv2.threshold(gr, 40, 150, cv2.THRESH_BINARY)
    
    
    #circles = cv2.HoughCircles(gr,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=30,maxRadius=100)  
    circles = cv2.HoughCircles(gr,cv2.HOUGH_GRADIENT,2,50)  
    circles = np.round(circles[0, :]).astype("int")
    
    centers =[]
    
    count = 0
    
    while (count < 2):
    
        for (x, y, r) in circles:
                    
            cv2.circle(gr, (x, y), r, (255,255,255), 8)
            
    #        cv2.rectangle(gr, (x - 2, y - 2), (x + 2, y + 2), (255,255,255), -1)
            
            temp_center = [x,y]
                        
            centers.append(temp_center)
            
            count = count + 1
            
    print min(centers[:][:])
    
    print max(centers[:][:])
    
    a = min(centers[:][:])
        
    b = max(centers[:][:])
        
    cv2.rectangle(gr, tuple(a), tuple(b), (0,0,0), 1, 1)
    
#    cv2.rectangle(th, tuple(a), tuple(b), (0,0,0), 1, 1)
    
#    autoROI = float(centers[0][0]), float(centers[0][1]), float(centers[1][0] - centers[0][0]), float(centers[1][1]-centers[0][1])
    
    autoROI = a[0], a[1], (b[0] - a[0]), (b[1] - a[1])
    
    print autoROI
    
    p1=int(autoROI[0]), int(autoROI[1])
    
    p2=int(autoROI[0]+autoROI[2]), int(autoROI[1]+autoROI[3])

    cv2.rectangle(gr, tuple(p1), tuple(p2), (0,0,0), 4, 4)
    
    tip = [(0,0)]

#    [pmax, new_autoROI] = markTip_AUTO(gr, th, centers, autoROI, tip)

    while(True):
    
        cv2.namedWindow("roi from circles", cv2.WINDOW_NORMAL)
            
        cv2.resizeWindow("roi from circles", 700,700)
            
        cv2.imshow("roi from circles", gr)    # grayscale image
    
        if cv2.waitKey(30) & 0xFF == ord('q'):
            
            break 
    
    cv2.destroyWindow("roi from circles")
    
#    autoROI= abs(np.array(autoROI))
#    
#    autoROI = tuple(autoROI)
    
    return centers, autoROI, th
    
#def connectROI(camera_, autoROI):
#        
#    bus = py2.BusManager()
#
#    c = py2.Camera()
#    
#    c.connect(bus.getCameraFromIndex(camera_))
#            
#    c.getFormat7Configuration()
#    
#    a = autoROI[2] - autoROI[0]
#    
#    b = autoROI[3] - autoROI[1]
#
#    fmt7imgSet = py2.Format7ImageSettings(0, autoROI[0], autoROI[1], a, b,  py2.PIXEL_FORMAT.MONO8)
#        
#    fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)
#    
#    c.startCapture()
#
#    return c
    
#def readROIFrame(c):
#
#image = c.retrieveBuffer()
#
##    print  " pixel format  " , image.getPixelFormat()
#
##    print " data stream" , image.getData()
#
##    print " ckhjdnbkjv" , len(image.getData())
#
##    print max(image.getData())
#
##    print min(image.getData())
#        
#gr = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) )
#
# 
#    #Image rgbImage;
#     #   rawImage.Convert( FlyCapture2::PIXEL_FORMAT_BGR, &rgbImage );
#       
#	#	// convert to OpenCV Mat
#		#int rowBytes = (double)rgbImage.GetReceivedDataSize()/(double)rgbImage.GetRows();       
#	#	cv::Mat image = cv::Mat(rgbImage.GetRows(), rgbImage.GetCols(), CV_8UC3, rgbImage.GetData(),rowBytes);
#       
#    #format_ = py2.PIXEL_FORMAT(py2.RGB8)
#    #rgbImage = image.convert(format_)
##    rowBytes = image_.getReceivedDataSize()/image_.getRows()
##    image_out = np.ndarray((image_.getRows(),image_.getCols(),3), np.uint8)
#    #image_out = np.asarray(image_.getRows(), image_.getCols(),  cv2.CV_8UC3,image_.getData(),rowBytes)
#
#
#a_bgr = cv2.cvtColor(gr, cv2.COLOR_GRAY2BGR)
#   
#a_bgr = cv2.medianBlur(a_bgr,5)
#
#gr = cv2.medianBlur(gr,5)
#
#return a_bgr, gr
            
        


    

def markTip_AUTO(gr, th, centers, autoROI, tip):
    
    
    # SCORRIMENTO ORIZZONTALE POI SCENDO
    pmax = (100,100)
    
    pvec = (0,0)
    
    for i in range (int(autoROI[1])+ 30,int(autoROI[1]+autoROI[3])-30, 2):
        
        for j in range (int(autoROI[0])+30,int(autoROI[0]+autoROI[2])-30, 2):
                    
            # check the value of the pixel
             
            if th[i][j] == 0 :
            
                p = i, j
                
                pvec = [pvec, p]
                
                
                
                # If the pixel is black, it is part of the Needle
                
                # Saving its coordinates
                
                #the maximum of the black pixel is the tip
            
    # Ouput: tip 2D-coordinates
    
    piy = pvec[-1][0]
    pix = pvec[-1][1]
    
    pi = pix,piy
        
    pmax = pi

    print ' x of the tip is: ', pmax[0], '   and y of the tip is: ', pmax[1]
        
    cv2.circle(gr, tuple(pmax) , 10, (255,255,255), -1)
        
    cv2.circle(th, tuple(pmax) , 10, (0,0,0), -1)
        
    autoROI = int(pmax[0] - 100), int(pmax[1] - 100), 100, 100
    
    print autoROI
    
    return pmax, autoROI
        
            
                
                
def trackShow_AUTO(gr, th):
    
        cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
        
        cv2.resizeWindow("Tracking", 700,700)
        
        cv2.imshow("Tracking", gr)    # grayscale image
        
        cv2.namedWindow("Th", cv2.WINDOW_NORMAL)

        cv2.resizeWindow("Th", 700,700)
        
        cv2.imshow("Th", th) # binary image
        
        
        
def boostUpdate_AUTO(c,tracker, ok, a_bgr, autoROI, centers, gr, th, tip):
        
        a_bgr, gr = readpyFrame(c)
        
#        if not ok:
#                
#                break
        
        # Update tracker passing the new frame. Output: new Bounding Box
    
        ok, autoROI = tracker.update(a_bgr)
        
        if ok:
            
            #Thresholding the grayscale image in a BINARY image: 0 or 255
            
            retval, th = cv2.threshold(gr, 40, 255, cv2.THRESH_BINARY)
                
            # Scanning every pixel of the moving ROI
                       
            pmax, autoROI = markTip_AUTO(gr, th, centers, autoROI, tip)
            
            tip.append(pmax)
                            
            trackShow_AUTO(gr,th)
            
        