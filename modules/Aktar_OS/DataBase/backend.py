import json
import asyncio
import websockets
import numpy as np
from time import sleep


class locEngine():
    def __init__(self):
        with open('walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.locs = np.arange(1, 100, 0.1)

    def find(self):
        pose_id = 0
        loc_id = 0
        while True:
            if pose_id > 7:
                pose_id = 0
            if loc_id > len(self.locs) - 1:
                loc_id = 0
            data = self.walking_model[pose_id]
            data["location"] = {"x": self.locs[loc_id], "z": 10}
            pose_id += 1
            loc_id += 1
            sleep(0.1)
            yield [data]

loc_engine = locEngine()
async def digital_twin(websocket):
    for data in loc_engine.find():
        try:
            await websocket.send(json.dumps({"data": data}))
        except websockets.exceptions.ConnectionClosedError:
            return


async def dt_serve():
    async with websockets.serve(digital_twin, "localhost", 5002):
        await asyncio.Future()

asyncio.run(dt_serve())
