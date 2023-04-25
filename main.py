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
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

base_options = core.BaseOptions(file_name='model.tflite', use_coral=False, num_threads=4)
classification_options = processor.ClassificationOptions(max_results=3, score_threshold=0.0)
options = vision.ImageClassifierOptions(base_options=base_options, classification_options=classification_options)
classifier = vision.ImageClassifier.create_from_options(options)
freeLED = LED(16)
busyLED = LED(26)

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

s=AngularServo(12, min_angle=-45, max_angle=45)
def setServoAngle(angle):
    s.angle=angle

aa=0

from datetime import datetime

while True:
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
        print("Started camera read")
    frame_buffer+=1
    image = frame
    image=image[40:490,25:]
#    cv2.imshow('Camera Feed',image)
    if counter==1:
        if aa<120:
            aa+=1
            continue
        cdatetimeunf=datetime.now()
        cdatetime=cdatetimeunf.strftime("%d-%B-%Y %H-%M-%S")
        folder="/home/pi/Trash-Segregator/static/images/"+cdatetimeunf.strftime("%Y")+"/"+cdatetimeunf.strftime("%B")
        file_name=cdatetime+".jpeg"
        file_path=os.path.join(folder,file_name)
        if not os.path.exists(folder):
           os.system('mkdir -p '+folder)
        cv2.imwrite(file_path,image)
        tensor_image=vision.TensorImage.create_from_file(file_path)
        categories = classifier.classify(tensor_image)
        bio=False
        for idx, category in enumerate(categories.classifications[0].categories):
           category_name = category.category_name
           score = round(category.score, 2)
           if category_name=='bio':
              bioScore=score
           if category_name=='non-bio':
              nonBioScore=score
        if bioScore>nonBioScore:
           bio=True
        elif bioScore<nonBioScore:
           bio=False
        print("b,nb",bioScore,",",nonBioScore)
        if bio:
            confidence=str(bioScore*100)
            print("Waste is Biodegradable")
            setServoAngle(-45)
            time.sleep(5)
            setServoAngle(0)
            new_name=file_name.replace(".jpeg","_Biodegradable.jpeg")
            new_name=confidence+"_"+new_name
            os.rename(file_path,os.path.join(folder,new_name))
        elif not bio:
            confidence=str(nonBioScore*100)
            print("Waste is Non-biodegradable")
            setServoAngle(45)
            time.sleep(5)
            setServoAngle(0)
            new_name=file_name.replace(".jpeg","_Non-Biodegradable.jpeg")
            new_name=confidence+"_"+new_name
            os.rename(file_path,os.path.join(folder,new_name))
        t_end=0
        first_time=0
        frame_buffer=0
        counter=0
        print("Waste segregated !")
        time.sleep(1)
        freeLED.on()


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
            c=max(contours,key=cv2.contourArea)
            mask = np.zeros(newThresh.shape[:2],np.uint8)
            new_image = cv2.drawContours(mask,[c],0,255,-1,)
            if cv2.contourArea(c)>1000 and len(contours)<=4:
                if counter==0:
                    busyLED.on()
                    freeLED.off()
                    print("Possible object detcted")
                    counter=1
                    aa=0
                    print("set counter to 1")
                    continue
    except Exception as e:
        print(e)
        pass
