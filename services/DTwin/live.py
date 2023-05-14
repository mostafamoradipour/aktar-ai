from time import time, sleep
from tqdm import tqdm
import base64
import pickle
import cv2

from modules.Aktar_AI.Pose.pose_estimation import PoseEstimator
from modules.Aktar_OS.DataBase.dt_db import DTdatabase
from modules.Aktar_AI.DTwin.dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1


class LiveDT():
    def __init__(self, cfg):
        self.estimator = PoseEstimator(cfg['pose_estimation'])
        self.database = DTdatabase(cfg['mongodb'])
        self.engine = DTEngine(cfg["engine"])
        self.vid1 = StreamerV1(cfg["stream"][0], max_queue_size=10)
        self.vid2 = StreamerV1(cfg["stream"][1], max_queue_size=10)
        # self.vid3 = StreamerV1(cfg["stream"][2])
        # with open('assets/all_frames_poses.pickle', 'rb') as handle:
        #     self.all_frames_poses = pickle.load(handle)

    def generator(self):
        self.vid1.thread.start()
        self.vid2.thread.start()
        while True:
            # start_time = time()
            ret1, frame1 = self.vid1.read_last()
            ret2, frame2 = self.vid2.read_last()
            if ret1 and ret2:
                frames = [frame1, frame2]
                num_cams = len(frames)
                all_cams_poses = self.estimator(frames)
                result = self.engine.step(frames, num_cams, all_cams_poses)
                # print(len(self.vid1.queue))
                self.database.update_count(result['person_current_count'])
                for person in result["persons"]:
                    dt_doc = {'id': person['id'], 'location': person['location'], 'height': person['height'], 'best_bodies': person['best_bodies']}
                    self.database.update_persons(dt_doc)
            else:
                break
            # print("dt engine: ", 1 / (time() - start_time))
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
            pickle.dump(all_frames_poses, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
