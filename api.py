from service_ba.personSearch import searchEngine
# from service_cs.ds_streaming import Streamer
from service_cs.streaming import Streamer
from flask import Flask, request, jsonify
from service_db.api_db import Database
from threading import Thread
from flask_cors import CORS
from waitress import serve
import argparse
import yaml


with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)
app = Flask(__name__)
CORS(app)
cam_col = Database(cfg["cam"]["mongodb"])
cdm_col = Database(cfg["cdm"]["mongodb"])
response_code = cfg["response_code"]
cdm_engine = searchEngine(cfg["cdm"])
trd = Thread(target=cdm_engine.search)
# trd.start()


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
        return jsonify({"persons": persons}), response_code["ok"]
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
        inputs = []
        for camera in cameras:
            play = camera["play"]
            # cam_col.update_one({"name": camera["name"]}, {"$set": {"play": play}})
            cam_col.remove_cam(camera["name"])
            cam_col.add_cam(camera)
            if play:
                inputs.append(camera["url"])
        if len(inputs):
            Streamer(inputs) 
        return {"message": "playing is done"}, response_code["ok"]
    except:
        {"message": "palying failed"}, response_code["bad_request"]


def create_app():
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--port", type=int,
                        default=5000, help="Port of serving api")
    args = parser.parse_args()
    # production server
    serve(app, host="0.0.0.0", port=args.port)
    # or in cmd: 
    #      waitress-serve --port=5000 --call api:create_app
    # development server
    # app.run(host='0.0.0.0', port=args.port)
