from modules.Aktar_AI.Pose.pose_estimation import PoseEstimator
from modules.Aktar_OS.DataBase.dt_db import DTdatabase
from modules.Aktar_AI.DTwin.dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1


class LiveDT():
    def __init__(self, cfg):
        self.estimator = PoseEstimator(cfg['pose_estimation'])
        self.database = DTdatabase(cfg['mongodb'])
        self.engine = DTEngine(cfg["engine"])
        self.vid1 = StreamerV1(cfg["stream"][0])
        self.vid2 = StreamerV1(cfg["stream"][1])
        self.vid1.thread.start()
        self.vid2.thread.start()

    def generator(self):
        while True:
            ret1, frame1 = self.vid1.read_last()
            ret2, frame2 = self.vid2.read_last()
            frames = [frame1, frame2]
            if ret1 and ret2:
                all_cams_poses = self.estimator(frames)
                result = self.engine.step(all_cams_poses)
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
