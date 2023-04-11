from modules.Aktar_OS.DataBase.dt_db import DTdatabase
from modules.Aktar_AI.DTwin.dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1
from time import sleep


class LiveDT():
    def __init__(self, cfg):
        self.engine = DTEngine(cfg["engine"])
        self.vid = StreamerV1(cfg["cam_url"])
        self.vid.thread.start()
        # self.vid = StreamerV1("assets/people2_2.avi")
        self.database = DTdatabase(cfg['mongodb'])

    def generator(self):
        while True:
            ret, frame = self.vid.read_last()
            if ret:
                result = self.engine.step(frame)
                if len(result["persons"]):
                    dt_doc = {
                        'id': 1, 'height': result["persons"][0]['height'], 'location': result["persons"][0]['location'], 'warning': result["persons"][0]['warning']}
                    self.database.update_dt(dt_doc)
            else:
                break
                # self.vid.release()
                # self.vid = StreamerV1("assets/people2_2.avi")
                # self.vid.thread.start()
            yield result
