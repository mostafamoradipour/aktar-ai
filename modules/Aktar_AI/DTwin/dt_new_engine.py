from copy import deepcopy
from time import time
import numpy as np
import random
import base64
import json
import cv2

from modules.Aktar_AI.DTwin.utils import euclidean_squared_distance, linear_assignment
from modules.Aktar_AI.DTwin.mapping import PointMapper
from modules.Aktar_AI.DTwin.demo_track import Track


random.seed(0)


class DTEngine():
    def __init__(self, cfg):
        '''
        '''
        with open(cfg['pose_data'], 'r') as f:
            self.pose_data = json.load(f)

        # Initialize mapper of all cameras
        self.mapper = PointMapper(cfg['mapping'])
        
        # Initialize per camera tracks
        self.camera_tracks = {}
        for cam_id in range(self.mapper.num_of_cams):
            self.camera_tracks[cam_id] = {}

        # Initialize global tracks
        self.tracks = {}

        self.msr_inf_cost = 15000
        self.trk_inf_cost = 2500
        self.deactive_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.list_of_colors = ["%06x" % random.randint(0, 0xFFFFFF) for _ in self.list_of_ids]

        self.congestion_map = np.zeros((40, 40), dtype="float") # for a 20 by 20 square meter place, resolution: 1 meter, stride = 0.5 meter
        self.warning_zones = cfg['warning_zones']

    def step(self, frames, all_cams_poses):
        '''
        TODO: Overal Algorithm:
            local measures should be matched with all global meaures and all tracks locations.
        '''

        # define current frame congestion map
        congestion_map = np.zeros((40, 40), dtype="float")

        # ----- # ---------------------------------------- #
        # PART-1: Tracking per camera. #
        # ----- # ---------------------------------------- #

        for cam_id in range(self.mappper.num_of_cams):

            # Fetch dets of camera tracks
            trk_dets = np.array([track.det for track in self.tracks[cam_id]])
            trk_ids = list(range(len(trk_dets)))

             # extract cam measurements
            cam_dets = all_cams_poses[cam_id]

            # Fetch dets of current frame (measurements)
            msr_dets = np.array([(det['box'], det['conf'], det['kpts'], det["confs"]) for det in cam_dets])
            # TODO: Filter detections
            msr_ids = list(range(len(msr_dets)))

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
                self.tracks[cam_id][trk_id].update(locations, height, msr_dets[msr_id])

            # create
            for msr_id in u_msr_ids:
                trk_id = self.list_of_ids.pop()
                global_msr_info[msr_id]["location"] = global_msr_location[msr_id]
                self.tracks[trk_id] = Track(trk_id, global_msr_info[msr_id])

            # miss
            for trk_id in u_trk_ids:
                self.tracks[trk_id].miss()

        # ----- # # -------------------------- #
        # PART-2: Make tracks and update them. #
        # ----- # # -------------------------- #
        trk_ids = list(self.tracks.keys())
        msr_ids = list(global_msr_info.keys())

        if not len(msr_ids):
            mached_ids, u_trk_ids, u_msr_ids = [], trk_ids, []
        elif len(trk_ids):
            # compute cost
            trk_locs = np.array([np.array(track.location_filter.x[:2]).reshape(2,) for track in self.tracks[cam_id].values()])
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
            self.tracks[trk_id] = Track(trk_id, global_msr_info[msr_id])

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
        result["person_current_count"] = len(self.tracks.values())
        for track in self.tracks.values():
            if not track.confirmed:
                continue
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["color"] = self.list_of_colors[track.id]
            data["best_bodies"] = []
            data["best_faces"] = []
            data["isFallen"] = track.isFallen
            data["isWalking"] = track.isWalking
            data["joints"] = []
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = self.warning_check(track.location)
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
