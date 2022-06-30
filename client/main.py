import itertools
import cv2
import os,time,sys
import numpy as np
import requests
camera = cv2.VideoCapture(0)

width = 512
height = 512
camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
first_time=0
frame_buffer=0
counter=0
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
time.sleep(1)
from gpiozero import AngularServo
def imageSubtract(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    return hsv
s=AngularServo(18, min_angle=-90, max_angle=90)
def setServoAngle(angle):
    s.angle=angle

URL = "http://192.168.1.115:8080/"
while True:
    if s.angle!=0:
        setServoAngle(0)
    _, frame = camera.read()
    if first_time==0:
        if frame_buffer<30:
            frame_buffer+=1
            continue
        refImg=frame
        refImg=refImg[40:490,25:]
        refThresh=imageSubtract(refImg)
        first_time=1
        frame_buffer=0
        print("Started camera read")
    frame_buffer+=1
    image = frame
    image=image[40:490,25:]
    newThresh=imageSubtract(image)
    key=cv2.waitKey(1)
    diff=cv2.absdiff(refThresh,newThresh)
    diff=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
    kernel=np.ones((5,5),np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
    diff=cv2.erode(diff,kernel,iterations = 2)
    diff=cv2.dilate(diff,kernel,iterations = 3)

    _, thresholded = cv2.threshold(diff, 0 , 255, cv2.THRESH_BINARY +cv2.THRESH_OTSU)
    contours, _= cv2.findContours(thresholded,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    try:
        blockPrint()
        c=max(contours,key=cv2.contourArea)
        enablePrint()
        mask = np.zeros(newThresh.shape[:2],np.uint8)
        new_image = cv2.drawContours(mask,[c],0,255,-1,)
        if cv2.contourArea(c)>1000 and len(contours)<=4:
            if counter==0:
                print("Possible object detcted")
                time.sleep(3)
                counter=1
                print("set counter to 1")
                continue
            else:
                print("counter is 1")
                files={}
                # for i in range(5):
                #     print("in loop")
                #     filename=str(i)+".jpg"
                #     time.sleep(0.5)
                #     print("writing image")
                #     cv2.imwrite(filename, image)
                #     files[str(i)]=open(filename,'rb')
                cv2.imwrite("toIdentify.jpeg", image)
                files["file"]=open("toIdentify.jpeg",'rb')
                bio=requests.post(url = URL, files = files).content.decode('ascii')
                print(bio)
                if bio=='True':
                    print("Waste is Biodegradable")
                    setServoAngle(-90)
                    time.sleep(5)
                    setServoAngle(0)
                elif bio=='False':
                    print("Waste is Non-biodegradable")
                    setServoAngle(90)
                    time.sleep(5)
                    setServoAngle(0)
                first_time=0
                frame_buffer=0
                counter=0
                print("Waste segregated !")
                time.sleep(1)
                # os.system("clear")
                continue
        
    except Exception as e:
        print(e)
        pass