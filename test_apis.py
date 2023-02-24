# import requests
from services.LogIN.login_request import client

# client = requests.session()

# Retrieve the CSRF token first
# sets cookie
client.get("https://api.kachrobotics.com/api/user/set_csrf_cookie/")
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']
else:
    # older versions
    csrftoken = client.cookies['csrf']

# loginRes = client.post(url="https://api.kachrobotics.com/api/user/login/", headers= {"Referer": "https://api.kachrobotics.com"},
#                         data= {"csrfmiddlewaretoken":csrftoken,  "email":"mostafa.moradipoor73@gmail.com", "password":"O64o4oo389"},)
# print(loginRes.status_code)
# print(loginRes.json())

uuidRes = client.post(url="https://api.kachrobotics.com/api/user/get_uuid/",  headers={
                   "Referer": "https://api.kachrobotics.com"}, data={"csrfmiddlewaretoken": csrftoken})
print(uuidRes.status_code)
uuid = uuidRes.json()["uuid"]
URL =  f"wss://api.kachrobotics.com/ws5/user/?uuid={uuid}"
print(URL)

#!/usr/bin/env python

import asyncio
import websockets

async def hello():
    async with websockets.connect(URL) as websocket:
        await websocket.send("Hello world!")
        await websocket.recv()

asyncio.run(hello())
