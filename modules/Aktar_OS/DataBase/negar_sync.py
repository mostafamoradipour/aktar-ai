# from services.LogIN.login_request import client
from services.DataBase.aktar_api import apiDB
from datetime import datetime
import websockets
import requests
import asyncio
import yaml


def sync_negar():
    # Define necessary databases 
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    # cam_col = apiDB(cfg["stream"]["mongodb"])
    # cdm_col = apiDB(cfg["cdm"]["mongodb"])
    # dt_col = apiDB(cfg["dt"]['mongodb'])

    client = requests.session()

    # Retrieve the CSRF token first
    client.get("https://api.kachrobotics.com/api/user/set_csrf_cookie/")  # sets cookie
    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
    else:
        # older versions
        csrftoken = client.cookies['csrf']

    loginRes = client.post(url="https://api.kachrobotics.com/api/user/login/", headers= {"Referer": "https://api.kachrobotics.com"},
                            data= {"csrfmiddlewaretoken":csrftoken,  "email":"mostafa.moradipoor73@gmail.com", "password":"O64o4oo389"},)
    print(loginRes.status_code)
    print(loginRes.json())

    # cam_url = 'https://api.kachrobotics.com/api/user/post_camera_stream/'
    # insight_url = 'https://api.kachrobotics.com/api/user/post_insight/'

    cdm_url = 'https://api.kachrobotics.com/api/user/customer_data/'
    res = client.delete(url=cdm_url, headers= {"Referer": "https://api.kachrobotics.com"})
    if res.status_code == 200:
        print("Negar CDM deleted!")
    print(res.json())

    # g_c = {}  # general counter
    # while True:
    #     # cameras = cam_col.get_docs()
    #     # public_cameras = []
    #     # for camera in cameras:
    #     #     del camera["play"]
    #     #     public_ip = requests.get('https://api.ipify.org').text
    #     #     local_ip = camera["url"].split("://")[1].split(":554")[0]
    #     #     camera["url"] = camera["url"].replace(local_ip, public_ip)
    #     #     public_cameras.append(camera)
    #     # res = requests.post(url=cam_url, json={
    #     #                     "csrfmiddlewaretoken":csrftoken, "cameras": public_cameras})
    #     # print("camera", res.status_code)
    #     persons = cdm_col.get_docs()
    #     public_persons = []
    #     for person in persons:
    #         _id = person["id"]
    #         if _id not in g_c.keys():
    #             g_c[_id] = {"face": 0, "body": 0, "time": 0}
    #         faces = [person[f"best_face_{count+1}"] for count in range(person["face_counter"])]
    #         bodies = [person[f"best_body_{count+1}"] for count in range(person["body_counter"])]
    #         times = person["time"]

    #         if len(faces) > g_c[_id]["face"] or len(bodies) > g_c[_id]["body"] or len(times) > g_c[_id]["time"]:
    #             public_person = {"id": _id, "faces": faces[g_c[_id]["face"]:],
    #                             "bodies": bodies[g_c[_id]["body"]:], "times": times[g_c[_id]["time"]:]}
    #             g_c[_id]["face"] = len(faces)
    #             g_c[_id]["body"] = len(bodies)
    #             g_c[_id]["time"] = len(times)
    #             public_persons.append(public_person)
    #     current_count = 0
    #     for person in persons:
    #         time = person["time"][-1]
    #         if datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp() > datetime.now().timestamp() - 5:
    #             current_count += 1
    #     # res = requests.post(url=insight_url, json={"csrfmiddlewaretoken":csrftoken, "count": current_count})
    #     print("count synced with negar: ", res.status_code)
    #     if len(public_persons):
    #         while True:
    #             record =  {"csrfmiddlewaretoken":csrftoken, "persons": public_persons}
    #             # res = requests.post(url=cdm_url, json=record)
    #             if res.status_code == 200:
    #                 print("CDM", res.status_code)
    #                 break


if __name__ == "__main__":
    sync_negar()

    # client = requests.session()

    # # Retrieve the CSRF token first
    # client.get("https://api.kachrobotics.com/api/user/set_csrf_cookie/")  # sets cookie
    # if 'csrftoken' in client.cookies:
    #     # Django 1.6 and up
    #     csrftoken = client.cookies['csrftoken']
    # else:
    #     # older versions
    #     csrftoken = client.cookies['csrf']

    # loginRes = client.post(url="https://api.kachrobotics.com/api/user/login/", headers= {"Referer": "https://api.kachrobotics.com"},
    #                         data= {"csrfmiddlewaretoken":csrftoken,  "email":"mostafa.moradipoor73@gmail.com", "password":"O64o4oo389"},)
    # print(loginRes.status_code)
    # print(loginRes.json())

    # uuidRes = client.post(url="https://api.kachrobotics.com/api/user/get_uuid/",  headers={
    #                 "Referer": "https://api.kachrobotics.com"}, data={"csrfmiddlewaretoken": csrftoken})
    # print(uuidRes.status_code)
    # uuid = uuidRes.json()["uuid"]
    # URL =  f"wss://api.kachrobotics.com/ws5/user/?uuid={uuid}"
    # print(URL)

    # async def hello():
    #     async with websockets.connect(URL) as websocket:
    #         print(websocket)
    #         print("done")
    #         # await websocket.send("Hello world!")
    #         # await websocket.recv()

    # asyncio.run(hello())
