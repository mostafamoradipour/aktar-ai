from flask import Flask, request, jsonify
from threading import Thread
from flask_cors import CORS
from waitress import serve
import websockets
import argparse
import asyncio
import yaml
import json
import os

from service_ba.personSearch import searchEngine
from service_cs.streamer import Streamer
from service_db.api_db import Database
from service_db.sync import sync_negar


with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)


app = Flask(__name__)
CORS(app)
cam_col = Database(cfg["cam"]["mongodb"])
cdm_col = Database(cfg["cdm"]["mongodb"])
cdm_col.reset()
os.system("rm -rf Faces/*")
print("CDM of Aktar deleted!")
response_code = cfg["response_code"]


async def cdm(websocket):
    cdm_engine = searchEngine(cfg["cdm"])
    async for message in websocket:
        message = json.loads(message)
        command = message["command"]
        if command == "get":
            cameras = cam_col.get_docs()
            await websocket.send(json.dumps({"cameras": cameras})) 
        elif command == "start":
            for camera in message["cameras"]:
                cdm_engine.cam_urls.append(camera["url"])
            cdm_engine.start()
        elif command == "stop":
            cdm_engine.stop()


async def cdm_serve():
    async with websockets.serve(cdm, "localhost", 5001):
        await asyncio.Future()


websocket_trd = Thread(target=asyncio.run, args=[cdm_serve()])
websocket_trd.start()


negar_sync_trd = Thread(target=sync_negar, args=[cam_col, cdm_col, cfg["email"]])
negar_sync_trd.start()


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
