
from service_jt.joint_detection import JointDetector
from service_dt.kf import static_kf, KalmanFilter
from service_cs.streaming import StreamerV1
from service_dt.mapping import PointMapper
from time import time
import numpy as np
import json


class DTEngine():
    def __init__(self, cfg, url):
        with open('service_dt/utils/walk-data.json', 'r') as f:
            self.walking_data = json.load(f)
        with open('service_dt/utils/standing.json', 'r') as f:
            self.standing_data = json.load(f) 
        self.detector = JointDetector(cfg["joint_detection"])
        self.mapper = PointMapper()
        self.vid = StreamerV1(url)
        self.height_kf = static_kf(init_state=180.)
        self.tracking_kf = KalmanFilter()

    def generator(self):
        pose_id = 0
        is_fallen = False
        location_shift = np.array([2.5, -.5])
        data = self.standing_data
        ms_location = None
        start_time = None
        while True:
            ret, frame = self.vid.read_last()
            if ret:
                poses, _ = self.detector.detect_one(frame)
                if len(poses):
                    ms_location, ms_height, posture = self.process_poses(poses)
                    if posture:
                        is_fallen = True if posture == "fall" else False
                    self.height_kf.step(ms_height)
                    self.tracking_kf.step(ms_location)
                    if self.tracking_kf.walking:
                        pose_id = (pose_id + 1) % 8
                        data = self.walking_data[pose_id]
                    else:
                        data = self.standing_data
            else:
                break
            x, z =  np.array(self.tracking_kf.x[:2]).reshape(-1) / 100 + location_shift
            data["location"] = {"x": x, "z": z}
            x, z =  np.array(self.tracking_kf.x[2:]).reshape(-1)
            data["direction"] = {"x": x, "z": z}
            data["isFallen"] = is_fallen
            # print(self.height_kf.state)
            # print(x, z)
            if ms_location:
                start_time = time()
            # stop
            if start_time:
                result = [data] if time() - start_time < 3 else []
            else:
                result = []
            yield result

    def process_poses(self, poses):
        joints = poses[0]
        neck, hip, ankle = self.simplify_joints(joints)

        posture = None
        if neck and hip:
            neck_hip_slope = abs((hip[1] - neck[1]) / (hip[0] - neck[0] + 1e-9))
            if neck_hip_slope < 0.5:
                posture = "fall"
            if neck_hip_slope > 2:
                posture = "stand"

        if hip and ankle:
            hip_ankle_slope = abs((ankle[1] - hip[1]) / (ankle[0] - hip[0] + 1e-9))
            if hip_ankle_slope < 0.5:
                posture = "fall"
            elif hip_ankle_slope > 2: 
                posture = "stand"

        if neck and ankle:
            neck_ankle_slope = abs((ankle[1] - neck[1]) / (ankle[0] - neck[0] + 1e-9))
            if neck_ankle_slope < 0.5:
                posture = "fall"
            elif neck_ankle_slope > 2:
                posture = "stand"

        location = self.mapper.map(ankle) if ankle else None
        height = self.mapper.height(location, neck) if location and neck and posture == "stand" else None

        return location, height, posture

    @staticmethod
    def simplify_joints(joints):
        """
        This method extracts neck, hip, and ankle points
        """
        neck = joints[0].tolist() if (joints[0] > 0).all() else None

        if (joints[5] > 0).all() and (joints[11] > 0).all():
            hip = ((joints[5] + joints[11]) / 2).tolist()
        elif (joints[5] > 0).all():
            hip = joints[5].tolist()
        elif (joints[11] > 0).all():
            hip = joints[11].tolist()
        else:
            hip = None

        if (joints[7] > 0).all() and (joints[13] > 0).all():
            ankle = ((joints[7] + joints[13]) / 2).tolist()
        elif (joints[7] > 0).all():
            ankle = joints[7].tolist()
        elif (joints[13] > 0).all():
            ankle = joints[13].tolist()
        else:
            ankle = None

        return neck, hip, ankle
