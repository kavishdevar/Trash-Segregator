from flask import Flask, render_template
import glob,os
import datetime
app = Flask(__name__)

@app.route('/')
def index():
    imageSrc=[]
    it=False
    files=list(filter(os.path.isfile, glob.iglob("/home/pi/Trash-Segregator/static/images" + '**/**/**/**')))
    files.sort(key=lambda x: os.path.getctime(x))
    files=reversed(files)
    for filename in files:
        ctime=os.path.getctime(filename)
        ctime=datetime.datetime.fromtimestamp(ctime).strftime("%m/%d/%Y, %H:%M:%S")
        confidence=os.path.basename(filename).split("_")[0]
        ctime=ctime + " (" + confidence + "%)"
        file=filename.replace("/home/pi/Trash-Segregator","")
        type=''
        if "_Biodegradable" in file:
            print("Found Biodegradable")
            imageSrc.append({"name":ctime,"type":"bio","filepath":file})
        elif "Non-Biodegradable" in file:
            print("Found Non-Biodegradable")
            imageSrc.append({"name":ctime,"type":"nonbio","filepath":file})
        else :
            print("Found Processing")
            imageSrc.append({"name":ctime,"type":"Processing","filepath":file})
        it=True
    if it:
       return render_template('index.html',images=imageSrc)
    else:
       return("No segregation done!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
