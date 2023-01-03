from flask import Flask, request, jsonify
from datetime import datetime
from threading import Thread
from flask_cors import CORS
from waitress import serve
import numpy as np
import websockets
import argparse
import asyncio
import yaml
import json
import os

from service_af.personSearch import searchEngine
from service_cs.streamer import streamEngine
# from service_dt.location import locEngine
# from service_db.sync import sync_negar
from service_db.db_api import Database
from service_dt.live import DTEngine

###############################################################################################

#-------------------------------------------Init-------------------------------------------#
with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

app = Flask(__name__)
CORS(app)
response_code = cfg["response_code"]
cam_col = Database(cfg["stream"]["mongodb"])
cdm_col = Database(cfg["cdm"]["mongodb"])
cdm_col.reset()
os.system("rm -rf Faces/*")
print("CDM of Aktar deleted!")
stream_engine = streamEngine()
cameras = cam_col.get_docs()
url = cameras[1]["url"]
loc_engine = DTEngine(cfg["dt"], url)
cdm_engine = searchEngine(cfg["cdm"])
#-------------------------------------------Init-------------------------------------------#

###############################################################################################

#-------------------------------------------Negar-------------------------------------------#
# # Negar Sync
# negar_sync_trd = Thread(target=sync_negar, args=[cam_col, cdm_col])
# negar_sync_trd.start()
#-------------------------------------------Negar-------------------------------------------#

###############################################################################################

#-------------------------------------------DT-------------------------------------------#
async def digital_twin(websocket):
    for data in loc_engine.generator():
        try:
            await websocket.send(json.dumps({"data": data}))
        except websockets.exceptions.ConnectionClosedError:
            return


async def dt_serve():
    async with websockets.serve(digital_twin, "localhost", 5002):
        await asyncio.Future()


dt_service_trd = Thread(target=asyncio.run, args=[dt_serve()])
dt_service_trd.start()
#-------------------------------------------DT-------------------------------------------#

###############################################################################################

#-------------------------------------------Stream-------------------------------------------#
# # Stream service based on websocket
# async def stream(websocket):
#     stream_engine = streamEngine()
#     async for message in websocket:
#         message = json.loads(message)
#         command = message["command"]
#         try:
#             if command == "start":
#                 for camera in message["cameras"]:
#                     stream_engine.cam_urls.append(camera["url"])
#                 stream_engine.start()
#                 message = "Stream service started successfully"
#                 print(message)
#                 await websocket.send(json.dumps({"message": message}))
#             elif command == "stop":
#                 stream_engine.stop()
#                 message = "Stream service stopped successfully"
#                 print(message)
#                 await websocket.send(json.dumps({"message": message}))
#             else:
#                 message = f"The command '{command}' not supported in Stream service of Aktar"
#                 print(message)
#                 await websocket.send(json.dumps({"message": message}))
#         except:
#             message = "You send a bad request"
#             print(message)
#             await websocket.send(json.dumps({"message": message}))


# async def sream_serve():
#     async with websockets.serve(stream, "localhost", 5002):
#         await asyncio.Future()


# stream_service_trd = Thread(target=asyncio.run, args=[sream_serve()])
# stream_service_trd.start()
#-------------------------------------------Stream-------------------------------------------#

###############################################################################################

#-------------------------------------------CDM-------------------------------------------#
async def cdm(websocket):
    async for message in websocket:
        message = json.loads(message)
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
                # await websocket.send(json.dumps({"message": message}))
        except:
            message = "You send a bad request"
            print(message)


async def cdm_serve():
    async with websockets.serve(cdm, "localhost", 5001):
        await asyncio.Future()


cdm_service_trd = Thread(target=asyncio.run, args=[cdm_serve()])
cdm_service_trd.start()
#-------------------------------------------CDM-------------------------------------------#

###############################################################################################

#-------------------------------------------REST-------------------------------------------#
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
            public_person = {"id": person["id"], "best_body": person[f'best_body_{person["body_counter"]}']}
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
        for person in persons:
            if person["id"] == _id:
                faces = [person[f"best_face_{count+1}"] for count in range(person["face_counter"])]
                bodies = [person[f"best_body_{count+1}"] for count in range(person["body_counter"])]
                times = person["time"]
                public_person = {"id": _id, "faces": faces, "bodies": bodies, "times": times}
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
        while not stream_engine.started: pass
        return {"message": "playing is done"}, response_code["ok"]
    except:
        return {"message": "palying failed"}, response_code["bad_request"]


@app.route("/stop", methods=["GET"])
def stop():
    stream_engine.stop()
#-------------------------------------------REST-------------------------------------------#

###############################################################################################

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
