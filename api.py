from flask import Flask, flash, request, send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from datetime import datetime
from flask_sock import Sock
from flask_cors import CORS
import argparse
import base64
import shutil 
import yaml
import json
import cv2
import os

from services.Stream.streamer import streamEngine
from services.DataBase.aktar_api import apiDB
from services.CDataM.manager import CDManager
from services.DTwin.live import LiveDT


ALLOWED_EXTENSIONS = {'glb'}
UPLOAD_FOLDER = 'glbs/'

app = Flask(__name__)
sock = Sock(app)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_PATH']


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Define necessary databases
with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

response_code = cfg["response_code"]
cam_col = apiDB(cfg["stream"]["mongodb"])
cdm_col = apiDB(cfg["cdm"]["mongodb"])
dt_col = apiDB(cfg["dt"]['mongodb'])
planes = []

# Reset the databases
cdm_col.reset()
dt_col.reset()
print("CDM and DT of Aktar reseted!")

# Initialize AI engines
stream_engine = streamEngine()
live_dt = LiveDT(cfg["dt"])
# live_dt.save_poses()
cdm_engine = CDManager(cfg["cdm"])


@app.route("/dt", methods=["GET"])
def get_dt_data():
    global planes
    files = []
    try:
        names = os.listdir(app.config['UPLOAD_FOLDER'])
        files = [ '/downloadfile/' + n for n in names]
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        print("-----------------------------------------------------")
    result = {'modelList': files, 'planeList': planes, 'warningZone': cfg["dt"]["engine"]["warning_zone"]}
    return jsonify(result), response_code["ok"]


@app.route('/downloadfile/<name>', methods=['GET'])
def download_file(name):
    if request.method == 'GET':
        return send_from_directory(app.config["UPLOAD_FOLDER"], name, as_attachment=True)


@app.route('/dt/reset', methods=['GET'])
def delete_file():
    global planes
    if request.method == 'GET': 
        planes = []
        # checking for folder availaibility using try and except block
        try:
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            print("We can see a folder deleted succesfully")
            print("-----------------------------------------------------")
            message = 'the directory deleted successfully.'
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            print("-----------------------------------------------------")
            message = 'the directory does not exist.'
        return {'message': message}, response_code['ok']


@app.route('/dt/add-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if not os.path.exists(app.config['UPLOAD_FOLDER']): # checking for folder existance
            # creating a new folder
            os.makedirs(app.config['UPLOAD_FOLDER']) 
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return 'No file part!'
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return 'No selected file!'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded successfully'


@app.route('/dt/set-plane', methods=['POST'])
def set_plane():
    global planes
    if request.method == 'POST':
        req = request.get_json()
        planes = req["planeList"]
        planes.extend(planes)
        return 'successful plane set'


@app.route("/frame", methods=["GET"])
def get_frame():
    # req = request.get_json()
    # try:
    #     cam_url = req["url"]
    #     assert isinstance(cam_url, str)
    # except:
    #     return {"message": "You send a bad request"}, response_code["bad_request"]
    try:
        cam = cv2.VideoCapture(cfg["dt"]["stream"][0])
        ret, frame = cam.read()
        assert ret, "failed to read the url"
        _, im_arr = cv2.imencode('.jpg', frame)
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()
        return jsonify({"frame": im_b64}), response_code["ok"]

    except:
        return {"message": "failed to read the url"}, response_code["bad_request"]


@sock.route('/cdm')
def cdm(ws):
    while True:
        message = json.loads(ws.receive())
        command = message["command"]
        try:
            if command == "start":
                cdm_engine.cam_urls = []
                for camera in message["cameras"]:
                    cdm_engine.cam_urls.append(camera["url"])
                cdm_engine.start()
                message = "CDM service started successfully"
                print(message)
            elif command == "stop":
                cdm_engine.stop()
                message = "CDM service stopped successfully"
                print(message)
            else:
                message = f"The command '{command}' not supported in CDM service of Aktar"
                print(message)
        except:
            message = "You send a bad request"
            print(message)


@sock.route('/dt')
def dt_live(ws):
    for data in live_dt.generator():
        # try:
        ws.send(json.dumps({"data": data}))
        # except websockets.exceptions.ConnectionClosedError:
        # return


@app.route("/get", methods=["GET"])
def get_cameras():
    try:
        cameras = cam_col.get_docs()
        return jsonify({"cameras": cameras}), response_code["ok"]
    except:
        return {"message": "Failed to load the cameras from database"}, response_code["bad_request"]


@app.route("/cdm", methods=["GET"])
def customer_data_manager():
    try:
        persons = cdm_col.get_docs()
        public_persons = []
        for person in persons:
            public_person = {
                "id": person["id"], "best_body": person[f'best_body_{person["body_counter"]}']}
            public_persons.append(public_person)
        return jsonify({"persons": public_persons}), response_code["ok"]
    except:
        return {"message": "Failed to load the customer info from database"}, response_code["bad_request"]


@app.route("/cdm_status", methods=["GET"])
def cdm_status():
    try:
        return jsonify({"cdm_status": cdm_engine.running}), response_code["ok"]
    except:
        return {"message": "Failed to load the customer info from database"}, response_code["bad_request"]


@app.route("/profile", methods=["POST"])
def profile_manager():
    req = request.get_json()
    _id = req["id"]
    try:
        persons = cdm_col.get_docs()
        dt_doc = dt_col.get_docs()
        if dt_doc:
            height = int(dt_col.get_docs()[0]['height'])
            trajectory = dt_col.get_docs()[0]['location_history']
        else:
            height = None
        for person in persons:
            if person["id"] == _id:
                faces = [person[f"best_face_{count+1}"]
                         for count in range(person["face_counter"])]
                bodies = [person[f"best_body_{count+1}"]
                          for count in range(person["body_counter"])]
                times = person["time"]

                trajectory = [{"location": {"x": 10, "z": 10}}, {"location": {"x": 1, "z": 1}}, {"location": {"x": 2, "z": 2}},
                              {"location": {"x": 3, "z": 3}}, {"location": {"x": 4, "z": 4}}, {"location": {"x": 3, "z": 5}},
                              {"location": {"x": 2, "z": 6}}, {"location": {"x": 1, "z": 5}}, {"location": {"x": 1, "z": 4}},
                              {"location": {"x": 2, "z": 3}}, {"location": {"x": 2, "z": 2}}, {"location": {"x": 2, "z": 1}}]

                public_person = {"id": _id, "faces": faces,
                                 "bodies": bodies, "times": times, "height": height,
                                 "trajectory": trajectory}
                break
        return jsonify({"persons": public_person}), response_code["ok"]
    except:
        return {"message": "Failed to load the customer info from database"}, response_code["bad_request"]


@app.route("/insight", methods=["GET"])
def insight_manager():
    try:
        persons = cdm_col.get_docs()
        current_count = 0
        for person in persons:
            time = person["time"][-1]
            if datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp() > datetime.now().timestamp() - 5:
                current_count += 1
        return jsonify({"person_current_count": current_count, "person_total_count": len(persons)}), response_code["ok"]
    except:
        return {"message": "Failed to load the customer info from database"}, response_code["bad_request"]


@app.route("/add", methods=["POST"])
def add_cameras():
    req = request.get_json()
    try:
        cameras = req["cameras"]
        assert isinstance(cameras, list)
        for camera in cameras:
            assert isinstance(camera["name"], str)
            assert isinstance(camera["url"], str)
            assert isinstance(camera["play"], bool)
    except:
        return {"message": "You send a bad request"}, response_code["bad_request"]
    try:
        for camera in cameras:
            name = camera["name"]
            url = camera["url"]
            play = camera["play"]
            camera = {"name": name, "url": url, "play": play}
            cam_col.remove_cam(name)
            cam_col.add_cam(camera)
        return {"message": "cameras added successfully"}, response_code["ok"]
    except:
        return {"message": "camera adding failed"}, response_code["bad_request"]


@app.route("/remove", methods=["POST"])
def remove_camera():
    req = request.get_json()
    try:
        name = req["name"]
    except:
        return {"message": "You send a bad request"}, response_code["bad_request"]
    try:
        cam_col.remove_cam(name)
        return {"message": "camera removed successfully"}, response_code["ok"]
    except:
        {"message": "camera removing failed"}, response_code["bad_request"]


@app.route("/play", methods=["POST"])
def play():
    req = request.get_json()
    try:
        cameras = req["cameras"]
        assert isinstance(cameras, list)
        for camera in cameras:
            assert isinstance(camera["name"], str)
            assert isinstance(camera["url"], str)
            assert isinstance(camera["play"], bool)
    except:
        return {"message": "You send a bad request"}, response_code["bad_request"]
    try:
        stream_engine.cam_urls = []
        for camera in cameras:
            play = camera["play"]
            cam_col.remove_cam(camera["name"])
            cam_col.add_cam(camera)
            if play:
                stream_engine.cam_urls.append(camera["url"])
        if len(stream_engine.cam_urls):
            stream_engine.start()
        while not stream_engine.opened:
            pass
        return {"message": "playing is done"}, response_code["ok"]
    except:
        return {"message": "palying failed"}, response_code["bad_request"]


@app.route("/stop", methods=["GET"])
def stop():
    stream_engine.stop()
    return {"message": "playing is stoped"}, response_code["ok"]


def create_app():
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--port", type=int,
                        default=5000, help="Port of serving api")
    args = parser.parse_args()
    # production server
    # serve(app, host="0.0.0.0", port=args.port)
    # or in cmd:
    #      waitress-serve --port=5000 --call api:create_app
    # development server
    app.run(host='0.0.0.0', port=args.port)
