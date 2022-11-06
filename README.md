# How to install Aktar

<h3>First make a new python environment and name it as you want:</h3>

`python3 -m env <Your Desired Name (for example "aktar_env")>`

Then activate the Aktar's python environment as follow:

`source <Your Python Env Path>/bin/activate`

<h3>Install the Aktar's prequirety packages in the activated environment:</h3>

`pip install -r requirements.txt`

<h3>Download pretrained weights of Detection and Recognition models from following links and put them in the right place:</h3>

Dowload the [pretrained weights](https://drive.google.com/file/d/18oenL6tjFkdR1f5IgpYeQfDFqU4w3jEr/view?usp=sharing) of detection model and convert it to onnx using [yolov5-face](https://github.com/deepcam-cn/yolov5-face) repository, then put the onnx model in `verification/detection/weights`

To covnert the pt model to onnx, in the yolov5-face repository run following command:

`python3 export.py --weights /path/to/the/pt/model`

Now, you can find the onnx model beside the pt model.

Put the [pretrained weights](https://drive.google.com/file/d/19I-MZdctYKmVf3nu5Da3HS6KH5LBfdzG/view) of recognition model in `verification/extraction/weights` (Extract the zip file. The rocognition model is named "w600k_mbf.onnx")

<h3>Then run the Aktar-Search API by running this command:</h3>

`python api.py`

<h3>Finally run the UI by running these commands:</h3>

`git clone git@github.com:YasharSL/Aktar.git UI`

`cd UI`

`git pull`

`git checkout 4e80ba55`

`npm install`

`npm run dev`
