from collections import deque
from copy import deepcopy
from time import time
import numpy as np
import base64
import cv2

from .kf import StaticKF, DynamicKF


def convert_to_jpeg(img):
    _, im_arr = cv2.imencode('.jpg', img)
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes).decode()
    return im_b64


class GTrack(object):
    best_body_scores = np.array([150, 100000, 2.6])
    max_body_scores = np.array([200.0, 100000, 4.0])

    def __init__(self, _id, msr_info):
        # use arguments
        self.id = int(_id)
        ms_locations = msr_info.pop("locations")
        if ms_locations:
            ms_location = np.array(ms_locations).mean(0)
        else:
            ms_location = np.array([50 * self.id, -100])
        self.features = msr_info.pop("features")
        info = msr_info.pop("info")
        bodies_scores = np.array([info[key].pop() for key in info.keys()])
        bodies = np.array([convert_to_jpeg(info[key].pop()) for key in info.keys()])
        self.info = info

        # initialize good bodies and their scores
        good_bodies_idx = [idx for idx in range(len(bodies)) if self.is_a_good_body(bodies_scores[idx])]
        self.good_bodies = deque([bodies[good_bodies_idx].tolist()])
        self.good_bodies_scores = bodies_scores[good_bodies_idx]
        self.best_bodies_scores = bodies_scores[good_bodies_idx]

        # initialize location and height
        self.location_filter = DynamicKF(init_location=ms_location)
        ms_heights = [self.info[cam_id][4] for cam_id in self.info.keys() if self.info[cam_id][4]]
        ms_height = np.array(ms_heights).mean() if ms_heights else None
        self.height_filter = StaticKF(init_height=ms_height)
        self._location = np.array(self.location_filter.x[:2]).reshape(-1)
        x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
        self.location = {"x": x, "z": z} # currnet location of track
        dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
        self.direction = {"x": dx, "z": dz} # currnet direction of track
        self.height = self.height_filter.x # current height of track

        # initialize other attributes
        self.update_time = time()
        self.pose_id = 8
        self.age = 1
        self.confirm_age = 30
        self.missed_count = 0
        self.max_missed_count = 20
        self.sln = 10 # standing location noise
        self.min_sln = 3
        self.max_sln = 15
        self.isFallen = False
        self.movement_index = 0

        self.update_fall_status()

    def update(self, msr_info):
        # use arguments
        ms_locations = msr_info.pop("locations")
        if ms_locations:
            ms_location = np.array(ms_locations).mean(0)
        elif self._location[1] < -20:
            ms_location = np.array([100 * self.id, -100])
        else:
            ms_location = self._location
        # self.features = msr_info.pop("features")
        features = msr_info.pop("features")
        self.features.extend(features)
        info = msr_info.pop("info")
        bodies_scores = np.array([info[key].pop() for key in info.keys()])
        bodies = np.array([convert_to_jpeg(info[key].pop()) for key in info.keys()])
        if self.confirmed:
            self.update_movement_index(deepcopy(info))
        self.info = info

        # update good bodies and their scores
        good_bodies_idx = [idx for idx in range(len(bodies)) if self.is_a_good_body(bodies_scores[idx])]
        better_bodies_idx = [idx for idx in good_bodies_idx if self.is_a_better_body(bodies_scores[idx])]
        self.good_bodies.append(bodies[better_bodies_idx].tolist())
        self.good_bodies_scores = bodies_scores[better_bodies_idx]
        self.best_bodies_scores = np.concatenate((self.best_bodies_scores, bodies_scores[better_bodies_idx]))

        # update location and height
        self.location_filter._update(np.array(ms_location).reshape((2, 1)))
        ms_heights = [self.info[cam_id][4] for cam_id in self.info.keys() if self.info[cam_id][4]]
        ms_height = np.array(ms_heights).mean() if ms_heights else None
        if ms_height:
            self.height_filter.update(ms_height)
            self.height = self.height_filter.x

        # update other attributes
        self.update_fall_status()
        if self.isWalking:
            self.sln = max(self.min_sln, self.sln - 2)
            self._location = np.array(self.location_filter.x[:2]).reshape(-1)
            x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
            self.location = {"x": x, "z": z}
            dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
            self.direction = {"x": dx, "z": dz}
            duration = time() - self.update_time
            if duration > 0.1:
                self.update_time = time()
                self.pose_id = (self.pose_id + 1) % 8
        else:
            self.pose_id = 8
            self.sln = min(self.max_sln, self.sln + 2)

        self.missed_count = max(0, self.missed_count - 1)
        self.age += 1

    def is_a_good_body(self, scores):
        intensity, area, aspect_ratio = scores
        if intensity < 50.0 or intensity > self.max_body_scores[0]:
            return False
        if area < 5000 or area > self.max_body_scores[1]:
            return False
        if aspect_ratio < 1.7 or aspect_ratio > self.max_body_scores[2]:
            return False
        return True

    def is_a_better_body(self, scores):
        if not len(self.best_bodies_scores):
            return True
        error = np.abs((scores - self.best_body_scores) / self.max_body_scores).sum()
        best_error = np.abs((self.best_bodies_scores - self.best_body_scores) / self.max_body_scores).min(axis=0).sum()
        return True if error < (best_error - 0.1) else False

    def update_movement_index(self, info):
        movements = np.array([])
        for key in info.keys():
            if key in self.info.keys():
                movements = np.append(movements, np.abs(info[key][0] - self.info[key][0]).sum())
        if len(movements):
            self.movement_index = np.mean([movements.max(), self.movement_index])
        else:
            # self.movement_index = np.max(0., self.movement_index - 10.)
            np.mean([0, self.movement_index])
 
    def update_fall_status(self):
        for key in self.info.keys():
            posture = self.info[key][3]
            if posture == "fall":
                self.isFallen = True
            if posture == "stand":
                self.isFallen = False

    def miss(self):
        self.missed_count += 1

    @property
    def active(self):
        return False if self.missed_count >= self.max_missed_count else True

    @property
    def confirmed(self):
        return True if self.age >= self.confirm_age else False

    @property
    def isWalking(self):
        return True if np.linalg.norm(self.location_filter.x[2:]) > self.sln and not self.isFallen else False
