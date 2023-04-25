# Trash-Segregator

## About

Trash-Segregator is a project that aims to automate the task of waste segregation in public dustbins by classifying waste as either recyclable or non-recyclable. The project uses a machine learning model to classify the waste and is trained on a dataset of images of recyclable and non-recyclable waste. The model is trained using the dataset from [here](https://www.kaggle.com/datasets/rayhanzamzamy/non-and-biodegradable-waste-dataset). The model is then converted to TFLite format which is a lightweight version of TensorFlow that is designed to run on raspberry pi. Using OpenCV the raspberry pi detects if waste has been kept. 
Then using a few servo motor the segregtion is done automatically.

## Rationale

Segregating an object to be discarded/thrown into biodegradable and non-biodegradable waste automatically results in non-biodegradable wastes like degraded plastics contaminating the soil and impacting biodiversity and soil health easily identifiable and hence preventing the issues listed above. Then further the biodegradable waste can be used to make natural manures and fertilizers which will increase the crop yield in agriculture and without decreasing the soil fertility.

##	Material Used
- Raspberry Pi 3
- USB Camera
- Servo motor
- Electrical wires
- Wooden blocks for the mechanical assembly

##	Procedure/ Description:
- Train the Model - train.py (Optional)
    - Download the entire dataset from https://www.kaggle.com/datasets/rayhanzamzamy/non-and-biodegradable-waste-dataset
    - Using `tflite_model_maker`, train the model
    - Install `tflite_model_maker` – `pip3 install tflite_model_maker`
    - Run the script `train.py`, from [here](https://www.tensorflow.org/lite/models/modify/model_maker/image_classification)
- Install dependencies
    - Setup Tensorflow Lite and OpenCV on raspberry pi `pip3 install tflite_runtime opencv`
    - Setup Flask on raspberry pi `pip3 install flask`
    - Setup gpiozero on raspberry pi `pip3 install gpiozero`
    OR
    - Install all the dependencies using `pip3 install -r requirements.txt`
- To start the Segregation program
    - Using OpenCV, detect objects in the camera stream
    - Capture and save image for analysis
    - Use classification function of Tensorflow Lite to classify into biodegradable and non-biodegradable
    - The Classification function returns a score for both the categories
    - The image is considered to be belong the category with the higher score, also a confidence score is calculated based on the type of the category the image falls into.
    - Save the image with a filename prefixed with the confidence score and suffixed with the category along with the date and time.
- Controlling the motor to tilt the base plate accordingly
    - The servo motor is set to 0° and programmed to rotate towards +45° (For Biodegradable) and -45 (For Non-Biodegradable).
    - The servo motor needs to be powered separately to drive, instead of the supply from the raspberry pi GPIO pins due to limitation of current. Note – Both the supply should have a common GND.
    - The servo motor used in the project is a 3-Pin MG996R which is commonly available.
    - The motor is controlled via PWM signals through one of the PWM GPIO pins of the raspberry pi (Here, GPIO 12 is used).
    - Using AngularServo class of gpiozero library which is usually preinstalled.
- HTTP Server Application to view segregation logs and images
    - The Flask application is hosted on the raspberry pi itself.
    - The python script uses Flask package to render a gallery of all the images captured along with the category and an overlay of the confidence score over each image.
    - The script is run on the raspberry pi and can be accessed from any device on the same network.


<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

## Credits

Great thanks to [rayhanzamzamy](https://www.kaggle.com/datasets/rayhanzamzamy/non-and-biodegradable-waste-dataset) (on Kaggle) for the dataset.

## References: 
1.	https://keras.io/examples/vision/image_classification_from_scratch/
2.	https://www.tensorflow.org/lite/
3.	https://teachablemachine.withgoogle.com/
4.	https://www.tensorflow.org/lite/models/modify/model_maker/image_classificaton 
5.	https://www.kaggle.com/datasets/rayhanzamzamy/non-and-biodegradable-waste-dataset