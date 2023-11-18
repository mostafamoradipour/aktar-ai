from copy import deepcopy
from time import time
import numpy as np
import random
import base64
import json
import cv2

from .utils import euclidean_squared_distance, linear_assignment, get_bodies1
from aktarai.mapping import PointMapper
from .gtrack import GTrack


random.seed(0)


class GTracker():
    def __init__(self, cfg):
        '''
        '''
        with open(cfg['pose_data'], 'r') as f:
            self.pose_data = json.load(f)
        self.mapper = PointMapper(cfg['mapping'])
        self.tracks = {}
        self.deactive_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.list_of_colors = ["%06x" % random.randint(0, 0xFFFFFF) for _ in self.list_of_ids]
        self.congestion_map = np.zeros((40, 40))
        self.warning_zones = cfg['warning_zones']
        self.msr_inf_cost = 15000
        self.trk_inf_cost = 5000

    def step(self, frames, all_cams_persons):
        '''
        TODO: Overal Algorithm:
            1- All camera detections must be matched with tracks.
            2- This matching can be done by:
                1 - Local matching based on per camera location, appearance, keypoints, and box. (Intra-camera matching)
                2 - Global matching based on overal location, and appearance. (Inter-camera matching)
                3- Start from a camera with more persons.
            3- Remaining detections must be merged with eachother based on location, appearance. (Inter-camera matching)
            4- Match merged detections with tracks based on new location.
            5- Make new tracks for unmatched detections.
        '''

        # Start from a camera with more persons
        # cam_id_list = sorted(range(self.mapper.num_of_cams), key=lambda index: len(all_cams_persons[index]), reverse=True)
        cam_id_list = sorted(range(self.mapper.num_of_cams), key=lambda index: len(all_cams_persons["detection"][index]["boxes"]), reverse=True)

        # define current frame heatmap
        congestion_map = np.zeros((40, 40))

        # ----- # ---------------------------------------- #
        # PART-1: Merge measurements of different cameras. #
        # ----- # ---------------------------------------- #
        global_msr_info = {}
        global_msr_location = {}
        current_global_id = 0
        iterator = {}

        for cam_id in cam_id_list:
            local_msr_info = {}
            local_msr_location = {}
             # extract cam measurements
            cam_persons = all_cams_persons["detection"][cam_id]
            if not len(cam_persons):
                continue
            
            # poses = np.array([person['kpts'] for person in cam_persons])
            # confs = np.array([person['cnfs'] for person in cam_persons])
            # boxes = np.array([person['box'] for person in cam_persons])
            poses = cam_persons["keypoints"]
            confs = cam_persons['confs']
            boxes = cam_persons['boxes']

            bodies, bodies_scores = get_bodies1(frames[cam_id].copy(), boxes, poses)

            # compute location for each cam measurement
            for _id, pose in enumerate(poses):
                conf = confs[_id]
                body = bodies[_id]
                body_scores = bodies_scores[_id]
                simp_pose = self.simplify_pose(pose, conf)
                neck, hip, ankle = simp_pose
                posture = self.process_pose(simp_pose)
                msr_location = self.mapper.imap(cam_id, ankle) if ankle else None
                if msr_location:
                    local_msr_location[_id] = np.array(msr_location)
                    msr_height = self.mapper.height(cam_id, msr_location, hip) if posture == "stand" else None
                    msr_height = 170.0
                    local_msr_info[_id] = [cam_id, pose, conf, simp_pose, posture, msr_location, msr_height, body, body_scores]

            # compare different cams measurements and aggregate them
            global_ids = list(global_msr_location.keys())  
            local_ids = list(local_msr_location.keys())

            if not len(local_ids):
                continue
            elif len(global_ids):
                # compute cost
                g_locs = np.array(list(global_msr_location.values()))
                l_locs = np.array(list(local_msr_location.values()))
                ccost = euclidean_squared_distance(g_locs, l_locs)
                # assingment
                matches, _, u_l_ids = linear_assignment(ccost, global_ids, local_ids, self.msr_inf_cost)
            else:
                matches, u_l_ids = [], local_ids

            # update
            for g_id, l_id in matches:
                g_l = global_msr_location[g_id]
                l_l = local_msr_location[l_id]
                if g_id in iterator.keys():
                    iterator[g_id] += 1
                else:
                    iterator[g_id] = 2
                global_msr_location[g_id] = g_l + 1 / iterator[g_id] * (l_l - g_l)
                cam_id = local_msr_info[l_id][0]
                global_msr_info[g_id][cam_id] = local_msr_info[l_id][1:]
                global_msr_info[g_id]["location"] = global_msr_location[g_id]

            # create
            for l_id in u_l_ids:
                global_msr_location[current_global_id] = local_msr_location[l_id]
                cam_id = local_msr_info[l_id][0]
                global_msr_info[current_global_id] = {cam_id: local_msr_info[l_id][1:]}
                global_msr_info[current_global_id]["location"] = global_msr_location[current_global_id]
                current_global_id += 1

        # ----- # # -------------------------- #
        # PART-2: Make tracks and update them. #
        # ----- # # -------------------------- #
        trk_ids = list(self.tracks.keys())
        msr_ids = list(global_msr_info.keys())

        # TODO: Add per camera matching -> this can cancel the location differences from different cameras for one person.

        if not len(msr_ids):
            mached_ids, u_trk_ids, u_msr_ids = [], trk_ids, []
        elif len(trk_ids):
            # compute cost
            trk_locs = np.array([np.array(track.location_filter.x[:2]).reshape(2,) for track in self.tracks.values()])
            msr_locs = np.array(list(global_msr_location.values()))
            ccost = euclidean_squared_distance(trk_locs, msr_locs)
            # assingment
            mached_ids, u_trk_ids, u_msr_ids = linear_assignment(ccost, trk_ids, msr_ids, self.trk_inf_cost)
        else:
            mached_ids, u_trk_ids, u_msr_ids = [], [], msr_ids

        # update
        for trk_id, msr_id in mached_ids:
            global_msr_info[msr_id]["location"] = global_msr_location[msr_id]
            self.tracks[trk_id].update(global_msr_info[msr_id])

        # create
        for msr_id in u_msr_ids:
            trk_id = self.list_of_ids.pop()
            global_msr_info[msr_id]["location"] = global_msr_location[msr_id]
            self.tracks[trk_id] = GTrack(trk_id, global_msr_info[msr_id])

        # miss
        for trk_id in u_trk_ids:
            self.tracks[trk_id].miss()

        # manage tracks and compute congestion map
        for trk_id in list(self.tracks.keys()):
            # tracks that are not matched with any detection
            track = self.tracks[trk_id]

            if not track.active:
                if track.confirmed:
                    self.deactive_tracks[trk_id] = track
                else:
                    self.list_of_ids.append(trk_id)
                self.tracks.pop(trk_id)
            else:
                # kalman predict
                track.location_filter._predict()

            # congestion map update
            if track.confirmed:
                x, z = track.location_filter.x[:2] // 50
                x, z = int(x), int(z)
                congestion_map[x, z] += 0.5
                if z > 0 and x > 0:
                    congestion_map[x - 1, z - 1] += 0.5
                    congestion_map[x - 1, z] += 0.5
                    congestion_map[x, z - 1] += 0.5
                elif z <= 0:
                    congestion_map[x - 1, z] += 0.5
                elif x <= 0:
                    congestion_map[x, z - 1] += 0.5

                if z < 9 and x < 9:
                    congestion_map[x + 1, z + 1] += 0.5
                    congestion_map[x + 1, z] += 0.5
                    congestion_map[x, z + 1] += 0.5
                elif z >= 9:
                    congestion_map[x + 1, z] += 0.5
                elif x >= 9:
                    congestion_map[x, z + 1] += 0.5

        # overal congestion map update
        congestion_map[congestion_map < 1] = 0.0
        self.congestion_map = congestion_map  + self.congestion_map -5 * np.array(congestion_map == 0) * np.array(self.congestion_map >= 5)

        # find congestion locations
        cong_locs = np.where(self.congestion_map > 25)

        # ----- # # -------------------- #
        # PART-3: Prepare result for UI. #
        # ----- # # -------------------- # 
        result = {"persons": [], "congestions": []}

        # add congestions
        for idx in range(len(cong_locs[0])):
            x = float(cong_locs[0][idx]) * 0.5 + 0.25
            z = float(cong_locs[1][idx]) * 0.5 + 0.25
            congestion = {"x": x, "z": z}
            result["congestions"].append(congestion)

        # add confirmed tracks
        result["person_current_count"] = 0
        for track in self.tracks.values():
            if not track.confirmed:
                continue
            result["person_current_count"] += 1
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["color"] = self.list_of_colors[track.id]
            data["best_bodies"] = track.good_bodies.tolist()
            data["best_faces"] = []
            data["isFallen"] = track.isFallen
            data["isWalking"] = track.isWalking
            data["joints"] = []
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = self.warning_check(track.location)
            data["movement_index"] = np.linalg.norm(list(track.direction.values()))
            result["persons"].append(data)

        return result

    def simplify_pose(self, pose, conf):
        """
        This method extracts neck, hip, and ankle points
        """
        neck = ((pose[5] + pose[6]) / 2).tolist() if (conf[5] > 0.5 and conf[6] > 0.5) else None
        hip = ((pose[11] + pose[12]) / 2).tolist() if (conf[11] > 0.5 and conf[12] > 0.5) else None
        ankle = ((pose[15] + pose[16]) / 2).tolist() if (conf[15] > 0.7 and conf[16] > 0.7) else None
        if ankle and hip:
            ankle[1] = ankle[1] + (ankle[1] - hip[1]) / 7.0
        return (neck, hip, ankle)

    def warning_check(self, location):
        x, z = location.values()
        for key in self.warning_zones:
            warning_zone = self.warning_zones[key]
            x1, z1, x2, z2 = warning_zone.values()
            if x > x1 and x < x2 and z > z1 and z < z2:
                return True
        return False

    def process_pose(self, simplified_pose):
        neck, hip, ankle = simplified_pose
        posture = None
        if hip and ankle:
            hip_ankle_slope = abs((ankle[1] - hip[1]) / (ankle[0] - hip[0] + 1e-9))
            if hip_ankle_slope < 0.5:
                posture = "fall"
            elif hip_ankle_slope > 4: 
                posture = "stand"
        return posture
