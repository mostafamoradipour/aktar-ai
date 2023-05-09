from time import sleep
from tqdm import tqdm
import pickle

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
        # self.vid3 = StreamerV1(cfg["stream"][2])
        # with open('assets/all_frames_poses.pickle', 'rb') as handle:
        #     self.all_frames_poses = pickle.load(handle)

    def generator(self):
        self.vid1.thread.start()
        self.vid2.thread.start()
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
            yield result

    def generator1(self):
        for idx in range(0, len(self.all_frames_poses), 5):
            all_cams_poses = self.all_frames_poses[idx]
            sleep(0.04*5)
            # all_cams_poses = all_cams_poses[1:2]
            result = self.engine.step(all_cams_poses)
            if len(result["persons"]):
                dt_doc = {
                    'id': 1, 'height': result["persons"][0]['height'], 'location': result["persons"][0]['location'], 'warning': result["persons"][0]['warning']}
                self.database.update_dt(dt_doc)
            yield result

    def save_poses(self):
        self.vid1.thread.start()
        self.vid2.thread.start()
        self.vid3.thread.start()
        all_frames_poses = []
        for idx in range(25*5*60):
            print(idx, len(self.vid1.queue))
            ret1, frame1 = self.vid1.read_first()
            ret2, frame2 = self.vid2.read_first()
            ret3, frame3 = self.vid3.read_first()
            frames = [frame1, frame2, frame3]
            if ret1 and ret2 and ret3:
                all_cams_poses = self.estimator(frames)
                all_frames_poses.append(all_cams_poses)
            else:
                break
        with open('assets/all_frames_poses.pickle', 'wb') as handle:
            pickle.dump(all_frames_poses, handle, protocol=pickle.HIGHEST_PROTOCOL)
