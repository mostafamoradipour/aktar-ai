from time import time
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
        self.vid1 = StreamerV1(cfg["stream"][0], max_queue_size=10, frame_skip=2)
        self.vid2 = StreamerV1(cfg["stream"][1], max_queue_size=10, frame_skip=2)
        self.vid3 = StreamerV1(cfg["stream"][2], max_queue_size=10, frame_skip=2)
        self.vid4 = StreamerV1(cfg["stream"][3], max_queue_size=10, frame_skip=2)
        with open('assets/all_frames_poses.pickle', 'rb') as handle:
            self.all_frames_poses = pickle.load(handle)

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
                self.database.update_count(result['person_current_count'])
                for person in result["persons"]:
                    dt_doc = {'id': person['id'], 'location': person['location'], 'height': person['height'],\
                                        'best_faces': person['best_faces'], 'best_bodies': person['best_bodies']}
                    self.database.update_persons(dt_doc)
            else:
                break
            # print("dt engine: ", 1 / (time() - start_time))
            yield result

    def demo(self):
        self.vid1.thread.start()
        self.vid2.thread.start()
        self.vid3.thread.start()
        self.vid4.thread.start()
        idx = 0
        while True:
            start_time = time()
            ret1, frame1 = self.vid1.read_first()
            ret2, frame2 = self.vid2.read_first()
            ret3, frame3 = self.vid3.read_first()
            ret4, frame4 = self.vid4.read_first()
            print(len(self.vid1.queue))
            if ret1 and ret2 and ret3 and ret4:
                idx += 2
                frames = [frame1, frame2, frame3, frame4]
                num_cams = len(frames)
                all_cams_poses = self.all_frames_poses[idx]
                result = self.engine.step(frames, num_cams, all_cams_poses)
                self.database.update_count(result['person_current_count'])
                for person in result["persons"]:
                    dt_doc = {'id': person['id'], 'location': person['location'], 'height': person['height'],\
                                        'best_faces': person['best_faces'], 'best_bodies': person['best_bodies']}
                    self.database.update_persons(dt_doc)
            else:
                break
            print("dt engine: ", 1 / (time() - start_time))
            yield result

    def save_poses(self):
        self.vid1.thread.start()
        self.vid2.thread.start()
        self.vid3.thread.start()
        self.vid4.thread.start()
        all_frames_poses = []
        for idx in range(25*5*60):
            ret1, frame1 = self.vid1.read_first()
            ret2, frame2 = self.vid2.read_first()
            ret3, frame3 = self.vid3.read_first()
            ret4, frame4 = self.vid4.read_first()
            frames = [frame1, frame2, frame3, frame4]
            if ret1 and ret2 and ret3 and ret4:
                print(idx, len(self.vid1.queue))
                all_cams_poses = self.estimator(frames)
                all_frames_poses.append(all_cams_poses)
            else:
                break
        with open('assets/all_frames_poses.pickle', 'wb') as handle:
            pickle.dump(all_frames_poses, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
