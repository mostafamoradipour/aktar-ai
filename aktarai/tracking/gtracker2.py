from copy import deepcopy
from time import time
import numpy as np
import base64
import json
import cv2

from .utils import euclidean_squared_distance, linear_assignment, get_bodies1, feature_euclidean_squared_distance, feature_cosine_distance
from aktarai.mapping import PointMapper
from .gtrack import GTrack


class GTracker2():
    def __init__(self, cfg):
        self.mapper = PointMapper(cfg['mapping'])
        self.tracks = {}
        self.deactive_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.msr_inf_loc_cost = 10000
        self.trk_inf_loc_cost = 10000
        self.trk_inf_feat_cost = 0.1

    def step(self, frames, detections, recognitions):
        # Start from a camera with more persons
        cam_id_list = sorted(range(self.mapper.num_of_cams), key=lambda index: len(detections[index]["boxes"]), reverse=True)

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
            cam_persons = detections[cam_id]
            cam_persons_feature = recognitions[cam_id]

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
                
                # msr_location = self.mapper.imap(cam_id, ankle) if ankle else None
                msr_location = self.mapper.imap2(cam_id, ankle, Y=0) if ankle else None
                if msr_location:
                    msr_location = (msr_location[0], msr_location[2])
                else:
                    msr_location = self.mapper.imap2(cam_id, hip, Y=100) if hip else None
                    if msr_location:
                        msr_location = (msr_location[0], msr_location[2])

                feature = cam_persons_feature[_id].reshape(-1)
                if msr_location:
                    local_msr_location[_id] = np.array(msr_location)
                    # msr_height = self.mapper.height(cam_id, msr_location, hip) if posture == "stand" else None
                    msr_height = 170.0
                    local_msr_info[_id] = [cam_id, pose, conf, simp_pose, posture, msr_location, msr_height, body, body_scores, feature]

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
                matches, _, u_l_ids = linear_assignment(ccost, global_ids, local_ids, self.msr_inf_loc_cost)
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
            loc_matched_ids, u_trk_ids, u_msr_ids = [], trk_ids, []
        elif len(trk_ids):
            # compute location cost
            trk_locs = np.array([np.array(track.location_filter.x[:2]).reshape(2,) for track in self.tracks.values()])
            msr_locs = np.array(list(global_msr_location.values()))
            ccost = euclidean_squared_distance(trk_locs, msr_locs)
            # assingment
            loc_matched_ids, u_trk_ids, u_msr_ids = linear_assignment(ccost, trk_ids, msr_ids, self.trk_inf_loc_cost)
        else:
            loc_matched_ids, u_trk_ids, u_msr_ids = [], [], msr_ids

        matched_ids = loc_matched_ids

        # compute feature matching for unmatched tracks and unmatched measures
        if len(u_msr_ids) and len(u_trk_ids):
            u_trk_features = np.array([np.array(self.tracks[trk_id].features).mean(0) for trk_id in u_trk_ids])
            u_msr_features = np.array([np.array([global_msr_info[_id][cam_id][-1] for cam_id in global_msr_info[_id].keys() if cam_id != "locations"]).mean(0) for _id in u_msr_ids])
            # ccost = feature_euclidean_squared_distance(u_trk_features, u_msr_features)
            ccost = feature_cosine_distance(u_trk_features, u_msr_features)
            # assingment
            feat_matched_ids, u_trk_ids, u_msr_ids = linear_assignment(ccost, u_trk_ids, u_msr_ids, self.trk_inf_feat_cost)

            matched_ids = matched_ids + feat_matched_ids

        # update tracks
        for trk_id, msr_id in matched_ids:
            global_msr_info[msr_id]["location"] = global_msr_location[msr_id]
            self.tracks[trk_id].update(global_msr_info[msr_id])

        # missed tracks
        for trk_id in u_trk_ids:
            self.tracks[trk_id].miss()
            if not self.tracks[trk_id].active:
                track = self.tracks.pop(trk_id)
                if track.confirmed:
                    self.deactive_tracks[trk_id] = track
                else:
                    self.list_of_ids.append(trk_id)

        # create new tracks
        for msr_id in u_msr_ids:
            trk_id = self.list_of_ids.pop()
            global_msr_info[msr_id]["location"] = global_msr_location[msr_id]
            self.tracks[trk_id] = GTrack(trk_id, global_msr_info[msr_id])

        # compute feature matching for unconfirmed tracks and deactive tracks
        uc_trk_ids = [trk_id for trk_id in self.tracks.keys() if not self.tracks[trk_id].confirmed]
        d_trk_ids = list(self.deactive_tracks.keys())
        if len(uc_trk_ids) and len(d_trk_ids):
            uc_trk_features = np.array([np.array(self.tracks[_id].features).mean(0) for _id in uc_trk_ids])
            d_trk_features = np.array([np.array(track.features).mean(0) for track in self.deactive_tracks.values()])
            # ccost = feature_euclidean_squared_distance(uc_trk_features, d_trk_features)
            ccost = feature_cosine_distance(uc_trk_features, d_trk_features)
            # assingment
            matched_ids, _, _ = linear_assignment(ccost, uc_trk_ids, d_trk_ids, self.trk_inf_feat_cost)

            # activate deactive tracks
            for uc_trk_id, d_trk_id in matched_ids:
                self.tracks[d_trk_id] = self.tracks.pop(uc_trk_id)
                d_track = self.deactive_tracks.pop(d_trk_id)
                self.tracks[d_trk_id].id = d_track.id
                self.tracks[d_trk_id].age += d_track.age
  
        # kalman predict
        for trk_id in list(self.tracks.keys()):
            if self.tracks[trk_id].active:
                self.tracks[trk_id].location_filter._predict()

    def simplify_pose(self, pose, conf):
        """
        This method extracts neck, hip, and ankle points
        """
        neck = ((pose[5] + pose[6]) / 2).tolist() if (conf[5] > 0.5 and conf[6] > 0.5) else None
        hip = ((pose[11] + pose[12]) / 2).tolist() if (conf[11] > 0.8 and conf[12] > 0.8) else None
        ankle = ((pose[15] + pose[16]) / 2).tolist() if (conf[15] > 0.7 and conf[16] > 0.7) else None
        if ankle and hip:
            ankle[1] = ankle[1] + (ankle[1] - hip[1]) / 7.0
        return (neck, hip, ankle)

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
