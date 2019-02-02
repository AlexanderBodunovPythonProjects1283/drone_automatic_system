import cv2
import os
import time
import math
import imutils
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

IM_WIDTH=1280
IM_HEIGHT=720
rect_radius_new=5
number_of_led=2
const_width_window=30



def find_points_x0_y0(a1,a2,b1,b2):
    x=int((b2-b1)/(a1-a2))
    y=int(a1*x+b1)
    return [x,y]

    

def calc_distance(x,y):
    return int(math.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2))
 
 
def calc_fit_points(i,j,different):
    try:
        a= (i[1]-j[1])/(i[0]-j[0])
    except:
        a= (i[1]-j[1])/0.0001
        
    b=i[1]-a*i[0]
    
    try:
        a_inv=1/a
    except:
        a_inv=1e6
    b1_inv=i[1]+a_inv*i[0]
    b2_inv=j[1]+a_inv*j[0]
    count=0
    for i in different:
        s=i[1]-a*i[0]-b
        s1=i[1]+a_inv*i[0]
        
        if s<const_width_window and s>-const_width_window and (s1-b1_inv)*(s1-b2_inv)<=0:
            count+=1
    return count
    

def find_different(arr):
    prev=[]
    for i in arr:
        checked=True
        for j in prev:
            #print("lll     "+str((i[0]-j[0])**2+(i[1]-j[1])**2))
            if ((i[0]-j[0])**2+(i[1]-j[1])**2 <160):
                checked=False
        if checked:
           prev.append(i)
    return prev

def find_a(x_0,x_1,y_0,y_1):
    try:
        return (x_1-y_1)/(x_0-y_0)
    except:
        return (x_1-y_1)/0.0001

def find_b(x_0,x_1,a):
    return x_1-a*x_0
         
     
index_=0
camera_type ='picamera'
if camera_type=="picamera":
    
    # Initialize Picamera and grab reference to the raw capture
    camera = PiCamera()
    camera.resolution = (IM_WIDTH,IM_HEIGHT)
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
    rawCapture.truncate(0)
    

    for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        index_+=1
        
        
        t1 = cv2.getTickCount()
        img = frame1.array
        masc=cv2.inRange(img,(200,200,200),(255,255,255))
        
        im2,contours,hierarchy=cv2.findContours(masc,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(masc,contours,-1,(0,255,0),3)
        
        resized = imutils.resize(masc, width=300)
        ratio = masc.shape[0] / float(resized.shape[0])
        
        count_=0
        
        arr_contours=[]
        for i in contours:
            if cv2.contourArea(i)>10:
                M = cv2.moments(i)
                try:
                    cX = int((M["m10"] / M["m00"]) * 1)
                    cY = int((M["m01"] / M["m00"]) * 1)
                except:
                    cX = int((M["m10"] / 0.0001) * 1)
                    cY = int((M["m01"] / 0.0001) * 1)
                arr_contours.append([cX,cY])
        
        different=find_different(arr_contours)
        print(different)
        
        with open("/home/pi/share/report.txt","w") as file:
            for coordinate in different:
                file.write(str(coordinate[0])+" "+str(coordinate[1])+"\n")
        
        rawCapture.truncate(0)
                    
            
        
    
        
    
    
    





