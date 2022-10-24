from time import sleep
import websockets
import asyncio
import json


async def my_func():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(json.dumps({"play": True}))
        sleep(5)
        await websocket.send(json.dumps({"play": False}))
        sleep(5)
        await websocket.send(json.dumps({"play": True}))


if __name__ == "__main__":
    asyncio.run(my_func())
