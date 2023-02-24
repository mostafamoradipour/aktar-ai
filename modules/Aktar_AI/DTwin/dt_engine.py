from modules.Aktar_AI.Joint.joint_detection import JointDetector
from modules.Aktar_AI.DTwin.kf import static_kf, KalmanFilter
from modules.Aktar_AI.DTwin.mapping import PointMapper
from copy import deepcopy
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
        # self.location_shift = [2.8, -.8]
        self.location_shift = [0, 0]
        self.times = {"start_time": None}
        self.trks = []

    def run(self, frame):
        data = self.standing_data.copy()
        ms_location = None
        poses, _ = self.detector.detect_one(frame)
        bones = []
        if len(poses):
            for joints in poses:
                if (joints[2] > 0).all() and (joints[3] > 0).all():
                    vector_8 = (joints[3]-joints[2]).tolist()
                    vector_8[0] = abs(vector_8[0])
                    bones.append({"id": 8, "vector": vector_8})
                if (joints[3] > 0).all() and (joints[4] > 0).all():
                    vector_9 = (joints[4]-joints[3]).tolist()
                    vector_9[0] = abs(vector_9[0])
                    bones.append({"id": 9, "vector": vector_9})
                if (joints[8] > 0).all() and (joints[9] > 0).all():
                    vector_16 = (joints[9]-joints[8]).tolist()
                    vector_16[0] = abs(vector_16[0])
                    bones.append({"id": 16, "vector": vector_16})
                if (joints[9] > 0).all() and (joints[10] > 0).all():
                    vector_17 = (joints[10]-joints[9]).tolist()
                    vector_17[0] = abs(vector_17[0])
                    bones.append({"id": 17, "vector": vector_17})

                if (joints[5] > 0).all() and (joints[6] > 0).all():
                    vector_23 = (joints[6]-joints[5]).tolist()
                    vector_23[0] = abs(vector_23[0])
                    bones.append({"id": 23, "vector": vector_23})
                if (joints[11] > 0).all() and (joints[12] > 0).all():
                    vector_28 = (joints[12]-joints[11]).tolist()
                    vector_28[0] = abs(vector_28[0])
                    bones.append({"id": 28, "vector": vector_28})
                # if (joints[8] > 0).all() and (joints[9] > 0).all():
                #     vector_16 = (joints[9]-joints[8]).tolist()
                #     vector_16[0] = abs(vector_16[0])
                #     bones.append({"id": 16, "vector": vector_16})
                # if (joints[9] > 0).all() and (joints[10] > 0).all():
                #     vector_17 = (joints[10]-joints[9]).tolist()
                #     vector_17[0] = abs(vector_17[0])
                #     bones.append({"id": 17, "vector": vector_17})

                ms_location, ms_height, posture, fall_location = self.process_joints(joints)
                # self.update_trks(ms_location, ms_height, posture, fall_location)
            if posture:
                self.is_fallen = True if posture == "fall" else False
            self.height_kf.step(ms_height)
            self.tracking_kf.step(ms_location)
            if self.tracking_kf.walking:
                self.pose_id = (self.pose_id + 1) % 8
                data = self.walking_data[self.pose_id]
            else:
                data = self.standing_data
            if fall_location:
                self.fall_location = fall_location
        if self.is_fallen:
            x, z = self.fall_location[0] / 100, self.fall_location[1] /  100
        else:
            x, z =  np.array(self.tracking_kf.x[:2]).reshape(-1) / 100
        data["location"] = {"x": x+self.location_shift[0], "z": z+self.location_shift[1]}
        dx, dz =  np.array(self.tracking_kf.x[2:]).reshape(-1)
        data["direction"] = {"x": dx, "z": dz}
        data["isFallen"] = self.is_fallen
        data["height"] = self.height_kf.state
        data["joints"] = bones
        if self.find_zone(x, z) == 1:
            data["warning"] = True
        else:
            data["warning"] = False

        data1 = deepcopy(data)
        data1["location"]["x"] = x + self.location_shift[0] + 2

        if ms_location:
            self.times["start_time"] = time()
        # stop
        if self.times["start_time"]:
            result = [data, data1] if time() - self.times["start_time"] < 2 else []
        else:
            result = []
        return result

    def update_trks(self, ms_location, ms_height, posture, fall_location):
        for trk in self.trks:
            if abs(trk.location - ms_location) < self.max_dp:
                pass

    def process_joints(self, joints):

        neck, hip, ankle = self.simplify_joints(joints)

        posture = None
        fall_location = None
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
            # if neck_ankle_slope < 0.5:
            #     posture = "fall"
            if neck_ankle_slope > 2:
                posture = "stand"

        location = self.mapper.map(ankle) if ankle else None
        fall_location = self.mapper.map(hip) if hip and posture == "fall" else None
        height = self.mapper.height(location, neck) if location and neck and posture == "stand" else None

        return location, height, posture, fall_location

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
