from threading import Thread
from time import sleep
import websockets
import asyncio
import json


class CDMEngine:
    def __init__(self) -> None:
        self.running = False
        self.count = 0

    def start(self):
        print("method start is running")
        self.trd = Thread(target=self.run)
        self.running = True
        self.trd.start()

    def run(self):
        while self.running:
            sleep(1)
            print("Mostafa", self.count)
            self.count += 1 

    def stop(self):
        print("method stop is running")
        self.running = False
        self.trd.join()


async def my_func(websocket):
    loop = CDMEngine()
    async for message in websocket:
        message = json.loads(message)
        if message["play"]:
            loop.start()
        else:
            loop.stop()


async def main():
    async with websockets.serve(my_func, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
