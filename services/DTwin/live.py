from modules.Aktar_OS.DataBase.dt_db import DTdatabase
from modules.Aktar_AI.DTwin.dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1


class LiveDT():
    def __init__(self, cfg, url):
        self.engine = DTEngine(cfg)
        self.vid = StreamerV1(url)
        # self.vid.thread.start()
        self.database = DTdatabase(cfg['mongodb'])

    def generator(self):
        self.vid.thread.start()
        while True:
            ret, frame = self.vid.read_last()
            if ret:
                result = self.engine.run(frame)
                if result:
                    dt_doc = {
                        'id': 1, 'height': result[0]['height'], 'location': result[0]['location'], 'warning': result[0]['warning']}
                    self.database.update_dt(dt_doc)
                    print("Warning: ", dt_doc["warning"])
                    # print("height: ", dt_doc["height"])
            else:
                break
            yield result
