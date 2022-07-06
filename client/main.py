import itertools
import cv2
import os,time,sys
import numpy as np
import requests
import signal
import sys
from os import system,popen
from gpiozero import AngularServo,LED
import time

freeLED = LED(16)
busyLED = LED(26)

def blockprinta():
    sys.stdout = open(os.devnull, 'w')

def enableprinta():
    sys.stdout = sys.__stdout__

def printa(a):
    print(a)
    blockprinta()
    if "max()" not in a:
        system('echo trashClient: \"' + str(a) + '\" | sudo tee /dev/kmsg')
    enableprinta()

def signal_handler(sig, frame):
   freeLED.off()
   busyLED.off()
   printa('Exiting')
   f=open("/home/pi/code_running.txt","r+")
   f.truncate(0)
   f.close()
   f=open("/home/pi/code_running.txt","w")
   f.write("False")
   f.close()
   sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

f=open("/home/pi/code_running.txt","r+")
printa("Truncating")
f.truncate(0)
f.close()
printa("Writing True")
fa=open("/home/pi/code_running.txt","w")
fa.write("True")
fa.close()

camera=cv2.VideoCapture(0)
width = 512
height = 512
camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

first_time=0
frame_buffer=0
counter=0

time.sleep(1)

def imageSubtract(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    return hsv

s=AngularServo(18, min_angle=-90, max_angle=90)
def setServoAngle(angle):
    s.angle=angle


ssid=popen("sudo iwgetid -r").read()
printa(ssid)
def getURL():
   print("In function")
   if "Devars" in ssid:
      printa("Devars")
      return "http://192.168.1.115:8080/"
   elif "laptop-9" in ssid:
      printa("laptop-9")
      return "http://192.168.37.1:8080"

URL = getURL()
printa(URL)
aa=0

while True:
    # print(aa)
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
        busyLED.off()
        freeLED.on()
        printa("Started camera read")
    frame_buffer+=1
    
    image = frame
    image=image[40:490,25:]

    if counter==1:
        if aa<120:
            aa+=1
            continue
        files={}
        cv2.imwrite("/home/pi/toIdentify.jpeg", image)
        files["file"]=open("/home/pi/toIdentify.jpeg",'rb')
        bio=requests.post(url = URL, files = files).content.decode('ascii')
        printa(bio)
        if bio=='True':
            printa("Waste is Biodegradable")
            setServoAngle(-55)
            time.sleep(5)
            setServoAngle(0)
        elif bio=='False':
            printa("Waste is Non-biodegradable")
            setServoAngle(55)
            time.sleep(5)
            setServoAngle(0)
        t_end=0
        first_time=0
        frame_buffer=0
        counter=0
        printa("Waste segregated !")
        time.sleep(1)
        freeLED.on()
        printa("counter is 1")
          


    newThresh=imageSubtract(image)
    diff=cv2.absdiff(refThresh,newThresh)
    diff=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
    kernel=np.ones((5,5),np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
    diff=cv2.erode(diff,kernel,iterations = 2)
    diff=cv2.dilate(diff,kernel,iterations = 3)

    _, thresholded = cv2.threshold(diff, 0 , 255, cv2.THRESH_BINARY +cv2.THRESH_OTSU)
    contours, _= cv2.findContours(thresholded,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    try:
        if counter==0:
            blockprinta()
            c=max(contours,key=cv2.contourArea)
            enableprinta()
            mask = np.zeros(newThresh.shape[:2],np.uint8)
            new_image = cv2.drawContours(mask,[c],0,255,-1,)
            if cv2.contourArea(c)>1000 and len(contours)<=4:
                if counter==0:
                    busyLED.on()
                    freeLED.off()
                    printa("Possible object detcted")
                    counter=1
                    aa=0
                    printa("set counter to 1")
                    continue
    except Exception as e:
        printa(e)
        pass
