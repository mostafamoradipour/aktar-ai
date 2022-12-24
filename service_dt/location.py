from service_af.verification.detection.person_detection import PersonDetector
from service_jt.joint_detection import JointDetector
from service_cs.streaming import StreamerV1
from .realPoints import real_points
from time import sleep
import numpy as np
import json
import yaml
import cv2


class locEngine_demo():
    def __init__(self):
        with open('service_dt/walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.locs = np.arange(0, 6.35, 0.1)

    def find(self):
        pose_id = 0
        loc_id = 0
        while True:
            sleep(0.1)
            if pose_id > 7:
                pose_id = 0
            data = self.walking_model[pose_id]
            if loc_id > len(self.locs) - 1:
                loc_id = 0
            z = self.locs[loc_id]
            x = 3
            if z > 5:
                data["fallen"] = True
            else:
                data["fallen"] = False
            data["location"] = {"x": x+2.5, "z": z-0.5}
            pose_id += 1
            loc_id += 1
            yield [data]


def find_distance_angle_box(tlbr):
    camera_alpha = 80 * np.pi / 180
    camera_beta = 45 * np.pi / 180
    camera_height = 0.8
    img_height = 1080
    img_width = 1920
    # camera_angle = 0 * np.pi / 180
    w = tlbr[2] - tlbr[0]
    point_x = tlbr[2] - w / 2
    point_y = tlbr[3]
    alpha = (point_x - img_width / 2) / img_width * camera_alpha
    beta = (point_y - img_height / 2) / img_height * camera_beta 
    z = camera_height * np.tan(np.pi / 2 - beta)
    x = -1 * z * np.tan(alpha)
    return x, z


class locEngine_box():
    def __init__(self, cfg, url):
        with open('service_dt/walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.detector = PersonDetector(cfg)
        self.url = url

    def find(self):
        pose_id = 0
        vid = StreamerV1(self.url)
        x, z = 0, 0
        while True:
            ret, frame = vid.read_last()
            if pose_id > 7:
                pose_id = 0
            data = self.walking_model[pose_id]
            _, boxes = self.detector.detect_one(frame, None)
            if boxes:
                x, z = find_distance_angle_box(boxes[0])
                z = z + 1.25
                x  = x + 2.5
            data["location"] = {"x": x+2.5, "z": z-0.5}
            pose_id += 1
            yield [data]


def find_distance_angle_joint(loc_i):
    camera_alpha = 80 * np.pi / 180
    camera_beta = 45 * np.pi / 180
    camera_height = 0.8
    img_height = 1080
    img_width = 1920
    # camera_angle = 0 * np.pi / 180
    point_x = loc_i[0]
    point_y = loc_i[1]
    alpha = (point_x - img_width / 2) / img_width * camera_alpha
    beta = (point_y - img_height / 2) / img_height * camera_beta 
    z = camera_height * np.tan(np.pi / 2 - beta)
    x = -1 * z * np.tan(alpha)
    return x, z


class LocationDetector(object):
    def __init__(self):
        with open('service_dt/calibration.yaml') as f:
            loadeddict = yaml.safe_load(f)
        mtx = loadeddict.get('camera_matrix')
        dist = loadeddict.get('dist_coeff')
        mtx = np.array(mtx)
        dist = np.array(dist)
        imagePoints = np.load('service_dt/imagePoints.npy').astype('float32')
        ret, rvec, tvec = cv2.solvePnP(real_points, imagePoints, mtx, dist)
        R, _ = cv2.Rodrigues(rvec)
        P = mtx @ np.hstack((R, tvec))
        self.Q = np.linalg.inv(np.concatenate((P[:, 0:1], P[:, 2:]), axis=1))

    def locate(self, loc_i):
        pixelPoint = np.array([loc_i[0], loc_i[1], 1])
        physicalPoint = self.Q @ pixelPoint
        physicalPoint = physicalPoint[:2] / physicalPoint[2]
        x, z = 4.8 - physicalPoint[0] / 100, 6.35 - physicalPoint[1] / 100
        return x , z


def find_if_fallen(poses, fallen):
    neck_found, hip_found, ankle_found = False, False, False
    if len(poses):
        pose = poses[0]
        if (pose[0] > 0).all():
            neck = pose[0]
            neck_found = True
        if (pose[5] > 0).all():
            hip = pose[5]
            if (pose[11] > 0).all():
                hip += pose[11]
                hip /= 2
            hip_found = True
        elif (pose[11] > 0).all():
            hip = pose[11]
            hip_found = True
        if (pose[7] > 0).all():
            ankle = pose[7]
            if (pose[13] > 0).all():
                ankle += pose[13]
                ankle /= 2
            ankle_found = True
        elif (pose[13] > 0).all():
            ankle = pose[13]
            ankle_found = True
    if neck_found and hip_found:
        neck_hip_slope = abs((hip[1] - neck[1]) / (hip[0] - neck[0]))
        if neck_hip_slope < 2:
            fallen = True
        elif neck_hip_slope > 100:
            fallen = False
    if hip_found and ankle_found:
        hip_ankle_slope = abs((ankle[1] - hip[1]) / (ankle[0] - hip[0]))
        if hip_ankle_slope < 2:
            fallen = True
        elif hip_ankle_slope > 100: 
            fallen = False
    if neck_found and ankle_found:
        neck_ankle_slope = abs((ankle[1] - neck[1]) / (ankle[0] - neck[0]))
        if neck_ankle_slope < 2:
            fallen = True
        elif neck_ankle_slope > 100:
            fallen = False
    return fallen


class locEngine_joint():
    def __init__(self, cfg, url):
        with open('service_dt/walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.detector = JointDetector(cfg)
        self.locator = LocationDetector()
        self.vid = StreamerV1(url)

    def find(self):
        pose_id = 0
        x, z = 0, 0
        fallen = False
        shift = [2.5, -.5]
        data = self.walking_model[pose_id]
        while True:
            ret, frame = self.vid.read_last()
            if ret:
                prev_x, prev_z = x, z
                poses, _ = self.detector.detect_one(frame)
                if len(poses):
                    pose = poses[0]
                    if (pose[7, :] > 0).all():
                        loc_i = pose[7, :]
                        if (pose[13, :] > 0).all():
                            loc_i += pose[13, :]
                            loc_i /= 2
                        x, z = self.locator.locate(loc_i)
                    elif (pose[13, :] > 0).all():
                        loc_i = pose[13, :]
                        x, z = self.locator.locate(loc_i)
                    # fallen = find_if_fallen(poses, fallen)
                    distance = (x - prev_x) ^ 2 + (z - prev_z) ^ 2
                    if not fallen and distance > 20 ^ 2:
                        pose_id += 1
                        if pose_id > 7:
                            pose_id = 0
                        data = self.walking_model[pose_id]
                        direction = [x - prev_x, z - prev_z]
                    if fallen:
                        direction = [x - prev_x, z - prev_z]
            else:
                break
            data["location"] = {"x": x+shift[0], "z": z+shift[1]}
            data["fallen"] = fallen
            # data["direction"] = direction
            yield [data]
