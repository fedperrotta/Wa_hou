# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 14:16:42 2018

@author: brain
"""

import cv2
import numpy as np

from headers import connectpyCapture, readpyFrame, circlesROI_AUTO, boostUpdate_AUTO  

def main(): 
    
    camera_ = 0
    
    c = connectpyCapture(camera_)
    
    a_bgr, gr = readpyFrame(c)

    centers, autoROI, th = circlesROI_AUTO(gr)
    
    tracker = cv2.TrackerBoosting_create()
    
#    c = connectROI(camera_, autoROI)
#    
#    a_bgr, gr = readROIFrame(c)
    
    # Tracking initialization passing the 1st frame and the selected ROI
            
    ok = tracker.init(a_bgr, autoROI)
    
    tip = [(0,0)]
                    
    while True:
    
        autoROI = boostUpdate_AUTO(c,tracker, ok, a_bgr, autoROI, centers, gr, th, tip)
                            
        if cv2.waitKey(20) & 0xFF == ord('q'):
            
            break 
        
    c.stopCapture()
    
    c.disconnect()
    
    cv2.destroyAllWindows()
    
    # Save tip coordinates in a text file for future uses

    np.savetxt('tipinROI_camera2.txt', tip)
    

    
if __name__ == "__main__":
    
    main()