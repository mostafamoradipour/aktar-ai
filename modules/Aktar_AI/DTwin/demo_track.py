from copy import deepcopy
from time import time
import numpy as np

from modules.Aktar_AI.DTwin.kf import StaticKF, DynamicKF


class Track(object):
    def __init__(self, _id, info):
        self.id = _id
        self.info = info
        ms_location = self.info.pop("location")
        self.location_filter = DynamicKF(init_location=ms_location)
        ms_heights = [self.info[cam_id][4] for cam_id in self.info.keys() if self.info[cam_id][4]]
        ms_height = np.array(ms_heights).mean() if ms_heights else None
        self.height_filter = StaticKF(init_height=ms_height)
        x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
        self.location = {"x": x, "z": z} # currnet location of track
        dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
        self.direction = {"x": dx, "z": dz} # currnet direction of track
        self.height = self.height_filter.x # current height of track

        self.update_time = time()
        self.pose_id = 8
        self.age = 1
        self.active = True
        self.confirm_age = 10
        self.confirmed = False
        self.missed_count = 0
        self.max_missed_count = 20
        self.sln = 10 # standing location noise
        self.min_sln = 3
        self.max_sln = 15
        self.isFallen = False
        self.movement_index = 0

    def update(self, info):
        ms_location = info.pop("location")

        # calculate and update all the attributes depending on this step and the previous one.
        if self.confirmed:
            self.update_movement_index(deepcopy(info))

        # calculate and update all the attributes depending on this step only.
        self.info = info
        self.location_filter._update(np.array(ms_location).reshape((2, 1)))
        ms_heights = [self.info[cam_id][4] for cam_id in self.info.keys() if self.info[cam_id][4]]
        ms_height = np.array(ms_heights).mean() if ms_heights else None
        if ms_height:
            self.height_filter.update(ms_height)
            self.height = self.height_filter.x

        if self.isWalking:
            self.sln = max(self.min_sln, self.sln - 2)
            x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
            self.location = {"x": x, "z": z}
            dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
            self.direction = {"x": dx, "z": dz}
            duration = time() - self.update_time
            if duration > 0.2:
                self.update_time = time()
                self.pose_id = (self.pose_id + 1) % 8
        else:
            self.pose_id = 8
            self.sln = min(self.max_sln, self.sln + 2)

        self.missed_count = max(0, self.missed_count - 1)
        self.age += 1
        if self.age >= self.confirm_age:
            self.confirmed = True

    def update_movement_index(self, info):
        movements = np.array([])
        for key in info.keys():
            if key in self.info.keys():
                movements = np.append(movements, np.abs(info[key][0] - self.info[key][0]).sum())
        if len(movements):
            self.movement_index = np.mean([movements.max(), self.movement_index])
        else:
            self.movement_index = np.max(0, self.movement_index - 10)

    def miss(self):
        self.missed_count += 2
        if self.missed_count >= self.max_missed_count:
            self.active = False

    @property
    def isWalking(self):
        return True if np.linalg.norm(self.location_filter.x[2:]) > self.sln and not self.isFallen else False
