from copy import deepcopy
from time import time
import numpy as np
import json

from modules.Aktar_AI.DTwin.utils.utils import euclidean_squared_distance2, linear_assignment
from modules.Aktar_AI.Pose.pose_estimation import PoseEstimator
from modules.Aktar_AI.DTwin.mapping import PointMapper
from modules.Aktar_AI.DTwin.track import Track


class DTEngine():
    def __init__(self, cfg):
        with open(cfg['pose_data'], 'r') as f:
            self.pose_data = json.load(f)
        self.estimator = PoseEstimator(cfg['joint_detection'])
        self.mapper = PointMapper(cfg['mapping'])
        self.tracks = {}
        self.missed_tracks = {}
        self.fallen_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.congestion_map = np.zeros((20, 20), dtype="float") # for a 10 by 10 square meter place, resolution: 1 meter, stride = 0.5 meter

    def step(self, frame):
        poses = self.estimator(frame)

        est_ids = list(range(len(poses)))
        trk_ids = list(self.tracks.keys())

        if len(est_ids) and len(trk_ids):
            prev_poses = np.array([track.pose for track in self.tracks.values()])
            cost = euclidean_squared_distance2(prev_poses, poses)            
            matches, u_trk_ids, u_est_ids = linear_assignment(cost, trk_ids, est_ids)
        else:
            matches, u_trk_ids, u_est_ids = [], trk_ids, est_ids

        for trk_id, est_id in matches:
            pose = poses[est_id]
            simplified_pose = self.simplify_pose(pose)
            neck, _, ankle = simplified_pose
            posture = self.process_pose(simplified_pose)
            ms_location = self.mapper.map(ankle) if ankle else None
            if not ms_location:
                u_trk_ids.append(trk_id)
                continue
            ms_height = self.mapper.height(ms_location, neck) if ms_location and neck and posture == "stand" else None
            self.tracks[trk_id].update(pose, ms_location, ms_height, posture)

            # update congestion map
            track = self.tracks[trk_id]
            if track.confirmed:
                x, z = track.location_filter.x[:2] // 50
                self.congestion_map[x, z] += 1.0
                if z > 0 or x > 0:
                    self.congestion_map[max(0, x-1), max(0, z-1)] += 0.75
                if z < 19 or x < 19:
                    self.congestion_map[min(x+1, 19), min(z+1, 19)] += 0.75

        for est_id in u_est_ids:
            pose = poses[est_id]
            simplified_pose = self.simplify_pose(pose)
            neck, _, ankle = simplified_pose
            posture = self.process_pose(simplified_pose)
            ms_location = self.mapper.map(ankle) if ankle else None
            if not ms_location:
                continue
            ms_height = self.mapper.height(ms_location, neck) if neck and posture == "stand" else None
            trk_id = self.list_of_ids.pop()
            self.tracks[trk_id] = Track(trk_id, pose, ms_location, ms_height)

        for trk_id in u_trk_ids:
            self.tracks[trk_id].missed()   

        for trk_id, track in self.fallen_tracks.copy().items():
            if time() - track.fall_time > 5:
                self.missed_tracks[trk_id] = track
                self.fallen_tracks.pop(trk_id)

        for trk_id, track in self.tracks.copy().items():
            if not track.active:
                if track.confirmed:
                    if track.isFallen:
                        track.fall_time = time()
                        self.fallen_tracks[trk_id] = track
                    else:
                        self.missed_tracks[trk_id] = track
                else:
                    self.list_of_ids.append(trk_id)
                self.tracks.pop(trk_id)

        # Congestion Alert
        self.congestion_map[self.congestion_map <= 1] = 0.0
        if self.congestion_map.sum() > 1:
            print("Congestion !!!")

        # Prepare result for UI
        result = []
        for track in self.tracks.values():
            if not track.confirmed:
                continue
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["isWalking"] = track.isWalking
            data["joints"] = [] if track.isWalking and not track.isFallen else self.extract_bones(track.pose)
            data["isFallen"] = track.isFallen
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = True if self.zone(track.location) == 1 else False
            result.append(data)
        for track in self.fallen_tracks.values():
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["isWalking"] = track.isWalking
            data["joints"] = [] if track.isWalking and not track.isFallen else self.extract_bones(track.pose)
            data["isFallen"] = track.isFallen
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = True if self.zone(track.location) == 1 else False
            result.append(data) 
        return result

    def process_pose(self, simplified_pose):
        neck, hip, ankle = simplified_pose
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
            # if neck_ankle_slope < 0.5:
            #     posture = "fall"
            if neck_ankle_slope > 2:
                posture = "stand"

        return posture

    def simplify_pose(self, pose):
        """
        This method extracts neck, hip, and ankle points
        """
        neck = pose[0].tolist() if (pose[0] > 0).all() else None

        if (pose[6] > 0).all() and (pose[12] > 0).all():
            hip = ((pose[6] + pose[12]) / 2).tolist()
        elif (pose[6] > 0).all():
            hip = pose[6].tolist()
        elif (pose[12] > 0).all():
            hip = pose[12].tolist()
        else:
            hip = None

        if (pose[8] > 0).all() and (pose[14] > 0).all():
            ankle = ((pose[8] + pose[14]) / 2).tolist()
        elif (pose[8] > 0).all():
            ankle = pose[8].tolist()
        elif (pose[14] > 0).all():
            ankle = pose[14].tolist()
        else:
            ankle = None

        return (neck, hip, ankle)

    def extract_bones(self, pose):
        bones = []
        if (pose[3] > 0).all() and (pose[4] > 0).all():
            vector_8 = (pose[4]-pose[3]).tolist()
            vector_8[0] = abs(vector_8[0])
            bones.append({"id": 8, "vector": vector_8})
        if (pose[4] > 0).all() and (pose[5] > 0).all():
            vector_9 = (pose[5]-pose[4]).tolist()
            vector_9[0] = abs(vector_9[0])
            bones.append({"id": 9, "vector": vector_9})
        if (pose[9] > 0).all() and (pose[10] > 0).all():
            vector_16 = (pose[10]-pose[9]).tolist()
            vector_16[0] = abs(vector_16[0])
            bones.append({"id": 16, "vector": vector_16})
        if (pose[10] > 0).all() and (pose[11] > 0).all():
            vector_17 = (pose[11]-pose[10]).tolist()
            vector_17[0] = abs(vector_17[0])
            bones.append({"id": 17, "vector": vector_17})
        if (pose[6] > 0).all() and (pose[7] > 0).all():
            vector_23 = (pose[7]-pose[6]).tolist()
            vector_23[0] = abs(vector_23[0])
            bones.append({"id": 23, "vector": vector_23})
        if (pose[12] > 0).all() and (pose[13] > 0).all():
            vector_28 = (pose[13]-pose[12]).tolist()
            vector_28[0] = abs(vector_28[0])
            bones.append({"id": 28, "vector": vector_28})

        return bones

    def zone(self, location):
        x, z =  location.values()
        if x > 2.5 and z > 4.5:
            return 1
        elif x < 2.5 and z > 4.5:
            return 2
        elif x < 2.5 and z < 4.5:
            return 3
        else:
            return 4
