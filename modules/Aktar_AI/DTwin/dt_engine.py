from modules.Aktar_AI.Joint.joint_detection import JointDetector
from modules.Aktar_AI.DTwin.kf import static_kf, KalmanFilter
from modules.Aktar_AI.DTwin.mapping import PointMapper
from time import time
import numpy as np
import json


class DTEngine():
    def __init__(self, cfg):
        with open(cfg['walking_data'], 'r') as f:
            self.walking_data = json.load(f)
        with open(cfg['standing_data'], 'r') as f:
            self.standing_data = json.load(f) 
        self.detector = JointDetector(cfg['joint_detection'])
        self.mapper = PointMapper(cfg['mapping'])
        self.height_kf = static_kf(init_state=180.)
        self.tracking_kf = KalmanFilter()
        self.pose_id = 0
        self.is_fallen = False
        self.location_shift = [2.8, -.8]
        self.times = {"start_time": None}

    def run(self, frame):
        data = self.standing_data.copy()
        ms_location = None
        poses, _ = self.detector.detect_one(frame)
        if len(poses):
            ms_location, ms_height, posture = self.process_poses(poses)
            if posture:
                self.is_fallen = True if posture == "fall" else False
            self.height_kf.step(ms_height)
            self.tracking_kf.step(ms_location)
            if self.tracking_kf.walking:
                self.pose_id = (self.pose_id + 1) % 8
                data = self.walking_data[self.pose_id]
            else:
                data = self.standing_data
        x, z =  np.array(self.tracking_kf.x[:2]).reshape(-1) / 100
        # print("location: ", x, z)
        data["location"] = {"x": x+self.location_shift[0], "z": z+self.location_shift[1]}
        dx, dz =  np.array(self.tracking_kf.x[2:]).reshape(-1)
        data["direction"] = {"x": dx, "z": dz}
        data["isFallen"] = self.is_fallen
        data["height"] = self.height_kf.state

        if self.find_zone(x, z) == 1:
            data["warning"] = True
        else:
            data["warning"] = False
        
        if ms_location:
            self.times["start_time"] = time()
        # stop
        if self.times["start_time"]:
            result = [data] if time() - self.times["start_time"] < 2 else []
        else:
            result = []
        return result

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

    @staticmethod
    def find_zone(x, z):
        if x > 2.5 and z > 4.5:
            return 1
        elif x < 2.5 and z > 4.5:
            return 2
        elif x < 2.5 and z < 4.5:
            return 3
        else:
            return 4
