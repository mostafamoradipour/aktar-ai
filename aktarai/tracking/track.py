from time import time
import numpy as np

from .kf import StaticKF, DynamicKF


class Track(object):
    def __init__(self,
                 trk_id,
                 cam_id,
                 pose,
                 body,
                 body_se,
                 face,
                 face_se,
                 ms_location,
                 ms_height,
                 ):
        self.id = trk_id
        self.poses = {cam_id: pose}
        self.best_body = {cam_id: body} if len(body) else {cam_id: []}
        self.best_body_error = {cam_id: body_se} if len(body) else {cam_id: np.Inf}
        self.best_face = {cam_id: face} if len(face) else {cam_id: []}
        self.best_face_error = {cam_id: face_se} if len(face) else {cam_id: np.Inf}

        self.location_filter = DynamicKF(init_location=ms_location)
        self.height_filter = StaticKF(init_height=ms_height)

        x, z = np.array(self.location_filter.x[:2], dtype='float64').reshape(-1) / 100
        self.location = {"x": x, "z": z} # currnet location of track
        dx, dz = np.array(self.location_filter.x[2:], dtype='float64').reshape(-1)
        self.direction = {"x": dx, "z": dz} # currnet direction of track
        self.height = self.height_filter.x # current height of track

        self.update_time = time()
        self.pose_id = 8
        self.age = 1
        self.min_age = 1
        self.missed_count = 0
        self.max_missed_count = 5
        self.sln = 10 # standing location noise
        self.max_sln = 15
        self.min_sln = 3
        self.confirmed = False
        self.isFallen = False
        self.fall_status = {"location": None, "direction": None, "time": None}

    def update(self, cam_id, pose, body, body_se, face, face_se, ms_location, ms_height):
        self.poses[cam_id] = pose

        if cam_id not in self.best_body_error.keys():
            self.best_body_error[cam_id] = np.Inf
        if len(body) and body_se < self.best_body_error[cam_id]:
            self.best_body[cam_id] = [body]
            self.best_body_error[cam_id] = body_se
        else:
            self.best_body[cam_id] = []

        if cam_id not in self.best_face_error.keys():
            self.best_face_error[cam_id] = np.Inf
        if len(face) and face_se < self.best_face_error[cam_id]:
            self.best_face[cam_id] = [face]
            self.best_face_error[cam_id] = face_se
        else:
            self.best_face[cam_id] = []

        self.location_filter._update(np.array(ms_location).reshape((2, 1)))

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

        self.age += 1
        if self.age >= 5:
            self.confirmed = True
        self.missed_count = 0

    def fall(self, cam_id, pose, fall_location, fall_direction):
        self.fall_status["time"] = time()
        self.poses[cam_id] = pose
        self.isFallen = True
        self.fall_status["location"] = fall_location
        self.fall_status["fall_direction"] = fall_direction

    def missed(self):
        self.missed_count += 1
        if self.missed_count >= self.max_missed_count:
            self.age = 0
            self.missed_count = 0

    @property
    def isWalking(self):
        return True if np.linalg.norm(self.location_filter.x[2:]) > self.sln and not self.isFallen else False

    @property
    def active(self):
        return True if self.age >= self.min_age else False
