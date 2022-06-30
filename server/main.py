import os
from flask import Flask as flask
from flask import request
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
#import matplotlib.pyplot as plt


def identify(file_name):
  model = load_model('model.h5', compile=False)
  data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
  image = Image.open(file_name)
  size = (224, 224)
  image = ImageOps.fit(image, size, Image.LANCZOS)
  image_array = np.asarray(image)
  normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
  data[0] = normalized_image_array
  prediction = model.predict(data)
  prediction = np.squeeze(prediction)
  prediction = (prediction - np.min(prediction)) / (np.max(prediction) - np.min(prediction))
  print(prediction)
  return prediction

UPLOAD_FOLDER = './static/'

app = flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(
  SECRET_KEY=os.urandom(24)
)

@app.route("/",methods=["POST"])
def manage_root():
  results=[]
  print(request.files)
  # for i in range(5):
  file = request.files['file']
  if os.path.exists("./static/toIdentify.jpeg"):
    if os.path.exists("./static/toIdentify_old.jpeg"):
      os.remove("./static/toIdentify_old.jpeg")
    os.rename("./static/toIdentify.jpeg","./static/toIdentify_old.jpeg")
  file.save(os.path.join(app.config['UPLOAD_FOLDER'], "toIdentify.jpeg"))
  pr=identify("./static/toIdentify.jpeg")
  if int(pr[0])>int(pr[1]):
    # print("Waste is Biodegradable")
    results.append("True")
  else:
    # print("Waste is Non-Biodegradable")
    results.append("False")
  BioN=0
  NonBioN=0
  for i in results:
    if i=="True":
      BioN+=1
    elif i=="False":
      NonBioN+=1
  if BioN>NonBioN:
    return "True"
  else:
    return "False"
if __name__ == "__main__":
  app.run('0.0.0.0',8080,True)
