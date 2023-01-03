from service_db.db_api import Database
from service_dt.live import DTEngine
import websockets
import asyncio
import json
import yaml


with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)
cam_col = Database(cfg["stream"]["mongodb"])
cameras = cam_col.get_docs()
url = cameras[1]["url"]
# url = "outpy.avi"
# loc_engine = locEngine_demo(cfg["cdm"]["body_detection"], url)
loc_engine = DTEngine(cfg["dt"], url)


async def digital_twin(websocket):
    for data in loc_engine.generator():
        try:
            await websocket.send(json.dumps({"data": data}))
        except websockets.exceptions.ConnectionClosedError:
            return


async def dt_serve():
    async with websockets.serve(digital_twin, "localhost", 5002):
        await asyncio.Future()


asyncio.run(dt_serve())
