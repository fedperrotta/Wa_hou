# -*- coding: utf-8 -*-
"""
Created on Wed May 30 18:43:31 2018

@author: brain
"""

import flycapture2 as fc2
import cv2
import numpy as np


def connectCapture(bool):
    
        c = fc2.Context()
            
        c.connect(*c.get_camera_from_index(bool))
        
        print "Connecting to  camera: " , bool
            
        print c.get_camera_info()
        
        if bool==0:
        
            c.set_format7_configuration(fc2.MODE_0, 800, 400, 800, 800, fc2.PIXEL_FORMAT_RGB8)
        
        else:
            
            c.set_format7_configuration(fc2.MODE_0, 860, 500, 800, 800, fc2.PIXEL_FORMAT_RGB8)
            
        
        c.start_capture()
        
        return c
        
def readFrame(c):
    
    im1 = fc2.Image()
    
    [c.retrieve_buffer(im1)]
    
    a_bgr = np.array(im1)
    
    a_bgr = cv2.medianBlur(a_bgr,5)
    
    gr = cv2.cvtColor(a_bgr, cv2.COLOR_BGR2GRAY)
    
    return a_bgr, gr
    
def guiROI(gr):

    cv2.namedWindow("roi", cv2.WINDOW_NORMAL)
    
    cv2.resizeWindow("roi", 800,800)
    
    bbox = cv2.selectROI( "roi", gr, False, False)
    
    cv2.destroyWindow("roi")
    
    return bbox
    

def printROI_GUI(bbox, gr, th):
    
    print "THIS IS : " , bbox
    
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
    
    cv2.rectangle(gr, tuple(n_o), tuple(s_e), (0,0,0), 1, 1)  
            
    cv2.rectangle(th, tuple(n_o), tuple(s_e), (0,0,0), 1, 1)  
    
    return n_o, n_e, s_o, s_e
    
def circlesROI_GUI(gr,th):
    
    circles = cv2.HoughCircles(gr,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=10,maxRadius=30)  
    
    circles = np.round(circles[0, :]).astype("int")
    
    centers =[]
    
    for (x, y, r) in circles:
                
        cv2.circle(gr, (x, y), r, (50, 100, 100), 6)
        cv2.rectangle(gr, (x - 2, y - 2), (x + 2, y + 2), (255,255,255), -1)
        
#        cv2.circle(th, (x, y), r, (50, 100, 100), 6)
#        cv2.rectangle(th, (x - 2, y - 2), (x + 2, y + 2), (255,255,255), -1)
        
        temp_center = [x,y]
                
#        temp_center = [circles[1][1], circles[1][2]]
        
        centers.append(temp_center)
            
    print centers
    
    print centers[0]
    print centers[1]
        
     
       
    cv2.rectangle(gr, tuple(centers[0]), tuple(centers[1]), (0,0,0), 1, 1) 
    
    cv2.rectangle(th, tuple(centers[0]), tuple(centers[1]), (0,0,0), 1, 1)
    
    

def markTip_GUI(gr, th, n_o, n_e, s_o, s_e):
    
    it=0
                
    pmax=(0,0)
                
    for i in range (n_o[0]+5,n_e[0]-5):
        
        for j in range(n_o[1]+5,s_o[1]-5):
            
            # check the value of the pixel
            
            if th[j][i]==0:
                            
                # If the pixel is black, it is part of the Needle
                
                # Saving its coordinates
                
                p=(i,j)
                                        
                #the maximum of the black pixel is the tip
                
                if p[1] > pmax[1] and it<1:
                    
                    pmax = p
                           
                    # Ouput: tip 2D-coordinates
                        
                    print ' x of the tip is: ', pmax[0], '   and y of the tip is: ', pmax[1]

                    cv2.circle(gr, tuple(pmax) , 10, (0,0,0), -1)
                    
                    cv2.circle(th, tuple(pmax) , 10, (0,0,0), -1)
                    
                    it = it + 1 
                    
                    return pmax,it 
                    
                    
def trackShow_GUI(gr, th):
        
        cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
        
        cv2.resizeWindow("Tracking", 800,800)
        
        cv2.imshow("Tracking", gr)    # grayscale image
        
        cv2.namedWindow("Th", cv2.WINDOW_NORMAL)

        cv2.resizeWindow("Th", 800,800)
        
        cv2.imshow("Th", th) # binary image
        
        
        
def boostUpdate_GUI(c,tracker, ok, a_bgr, bbox, gr, tip):
 
        a_bgr, gr = readFrame(c)
        
#        if not ok:
#                
#                break
        
        # Update tracker passing the new frame. Output: new Bounding Box
    
        ok, bbox = tracker.update(a_bgr)
        
        if ok:
            
            #Thresholding the grayscale image in a BINARY image: 0 or 255
            
            retval, th = cv2.threshold(gr, 20, 255, cv2.THRESH_BINARY)
            
            n_o, n_e, s_o, s_e = printROI_GUI(bbox, gr, th)
            
            circlesROI_GUI(gr,th)
    
            # Scanning every pixel of the moving ROI
            
            pmax, it = markTip_GUI(gr, th, n_o, n_e, s_o, s_e)
                            
            tip.append(pmax)
            
            trackShow_GUI(gr,th)