from flask import Flask as flask
from flask import request
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
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
import platform
def getUploadFolder():
  if platform.system()=="Windows":
    return r'.\static'
  else:
    return './static'

UPLOAD_FOLDER = getUploadFolder()

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
  identifyPath=os.path.normpath("./static/toIdentify.jpeg")
  oldPath=os.path.normpath("./static/toIdentify_old.jpeg")
  if os.path.exists(identifyPath):
    if os.path.exists(oldPath):
      os.remove(oldPath)
    os.rename(identifyPath,oldPath)
  file.save(identifyPath)
  pr=identify(identifyPath)
  if int(pr[0])>int(pr[1]):
    print("Waste is Biodegradable")
    return True
  else:
    print("Waste is Non-Biodegradable")
    return False
if __name__ == "__main__":
  app.run('0.0.0.0',8080,True)
