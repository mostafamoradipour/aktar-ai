import numpy as np

from modules.Aktar_AI.DTwin.kf import StaticKF, DynamicKF


class Track(object):
    def __init__(self,
                 _id,
                 pose,
                 ms_location,
                 ms_height
                 ):
        self.id = _id
        self.pose = pose
        self.location_filter = DynamicKF(init_location=ms_location)
        self.height_filter = StaticKF(init_height=ms_height)

        x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
        self.location = {"x": x, "z": z} # currnet location of track
        dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
        self.direction = {"x": dx, "z": dz} # currnet direction of track
        self.height = self.height_filter.x # current height of track

        self.pose_id = 8
        self.age = 1
        self.min_age = 1
        self.missed_count = 0
        self.max_missed_count = 3
        self.sln = 10 # standing location noise
        self.max_sln = 15
        self.min_sln = 3
        self.confirmed = False
        self.isFallen = False

    def update(self, pose, ms_location, ms_height, posture):
        self.pose = pose
        self.location_filter.update(ms_location)

        if ms_height:
            self.height_filter.update(ms_height)
            self.height = self.height_filter.x

        if self.isWalking:
            self.sln = max(self.min_sln, self.sln - 2)
            x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
            self.location = {"x": x, "z": z}
            dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
            self.direction = {"x": dx, "z": dz}
            self.pose_id = (self.pose_id + 1) % 8
        else:
            self.pose_id = 8
            self.sln = min(self.max_sln, self.sln + 2)

        self.age += 1
        if self.age >= 5:
            self.confirmed = True
        self.missed_count = 0

        if posture:
            self.isFallen = True if posture == "fall" else False

    def missed(self):
        self.missed_count += 1
        if self.missed_count >= self.max_missed_count:
            self.age = 0
            self.missed_count = 0

    @property
    def isWalking(self):
        return True if np.linalg.norm(self.location_filter.x[2:]) > self.sln else False

    @property
    def active(self):
        return True if self.age >= self.min_age else False
