import numpy as np

from .utils import euclidean_squared_distance, linear_assignment, get_bodies_data, feature_cosine_distance, is_a_good_body
from aktarai.mapping import PointMapper
from .gtrack3 import GTrack


class GTracker():
    def __init__(self, cfg):
        self.mapper = PointMapper(cfg['mapping'])
        self.tracks = {}
        self.deactive_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.msr_inf_loc_cost = 10000
        self.msr_inf_feat_cost = 0.1
        self.trk_inf_loc_cost = 10000
        self.trk_inf_feat_cost = 0.1

    def step(self, frames, detections, recognitions):
        # TODO: Add per camera matching -> this can cancel the location differences from different cameras for one person.
        # TODO: Use all distances between each two camera measures pair to merge them (now we start from the camera with
        #       more measures and calculate the distance of measures of new cameras with the mean of previous ones).
        # TODO: Use all feature history of tracks to calculate the appearance matching
        # TODO: To do appearance matching between person with same direction (we must calulate the direction of persons)

        # Start from a camera with more persons
        cam_id_list = sorted(range(self.mapper.num_of_cams), key=lambda index: len(detections[index]["boxes"]), reverse=True)

        # ----- # ---------------------------------------- #
        # PART-1: Merge measurements of different cameras. #
        # ----- # ---------------------------------------- #
        global_msr_info = {}
        current_global_id = 0

        for cam_id in cam_id_list:
            local_msr_info = {}
             # extract cam measurements
            cam_persons_detection = detections[cam_id]
            cam_persons_feature = recognitions[cam_id]

            poses = cam_persons_detection["keypoints"]
            confs = cam_persons_detection['confs']
            boxes = cam_persons_detection['boxes']

            bodies, bodies_scores, simp_poses, bodies_posture = get_bodies_data(frames[cam_id].copy(), boxes, poses, confs)

            # compute location for each cam measurement
            for _id, pose in enumerate(poses):
                conf = confs[_id]
                body = bodies[_id]
                body_scores = bodies_scores[_id]
                simp_pose = simp_poses[_id]
                neck, hip, ankle = simp_pose
                posture = bodies_posture[_id]

                if self.mapper.mapping_data[cam_id]:
                    # msr_location = self.mapper.imap(cam_id, ankle) if ankle else None
                    if ankle:
                        msr_location = self.mapper.imap2(cam_id, ankle, Y=0)
                        msr_location = (msr_location[0], msr_location[2])
                    elif hip:
                        msr_location = self.mapper.imap2(cam_id, hip, Y=100) if hip else None
                        msr_location = (msr_location[0], msr_location[2])
                    else:
                        msr_location = None
                    if msr_location and neck:
                        X, Z = msr_location
                        msr_height = self.mapper.imap2(cam_id, neck, X=X, Z=Z)
                        msr_height = msr_height[1]
                    else:
                        msr_height = None
                else:
                    msr_location = None
                    msr_height = None

                if is_a_good_body(body_scores):
                    feature = [cam_persons_feature[_id].reshape(-1)]
                else:
                    feature = None

                if msr_location or feature:
                    # msr_height = 175.0
                    local_msr_info[_id] = {"location": msr_location, "feature": feature}
                    local_msr_info[_id]["info"] = {cam_id: [pose, conf, simp_pose, posture, msr_height, body, body_scores]}

            # compare different cams measurements and aggregate them
            global_loc_ids = [_id for _id in global_msr_info.keys() if global_msr_info[_id]["locations"]]  
            local_loc_ids = [_id for _id in local_msr_info.keys() if local_msr_info[_id]["location"]]
            global_feat_ids = [_id for _id in global_msr_info.keys() if global_msr_info[_id]["features"]] 
            local_feat_ids = [_id for _id in local_msr_info.keys() if local_msr_info[_id]["feature"]] 

            if len(global_loc_ids) and len(local_loc_ids):
                # compute cost
                g_locs = np.array([np.array(global_msr_info[_id]["locations"]).mean(0) for _id in global_loc_ids])
                l_locs = np.array([local_msr_info[_id]["location"] for _id in local_loc_ids])
                ccost = euclidean_squared_distance(g_locs, l_locs)
                # assingment
                loc_matches, _, u_l_loc_ids = linear_assignment(ccost, global_loc_ids, local_loc_ids, self.msr_inf_loc_cost)
            else:
                loc_matches, u_l_loc_ids = [], local_loc_ids

            if len(global_feat_ids) and len(local_feat_ids):
                # compute cost
                g_feats = np.array([np.array(global_msr_info[_id]["features"]).mean(0) for _id in global_feat_ids])
                l_feats = np.array([local_msr_info[_id]["feature"][0] for _id in local_feat_ids])
                ccost = feature_cosine_distance(g_feats, l_feats)
                # assingment
                feat_matches, _, u_l_feat_ids = linear_assignment(ccost, global_feat_ids, local_feat_ids, self.msr_inf_feat_cost)
            else:
                feat_matches, u_l_feat_ids = [], local_feat_ids

            matches = list(set(loc_matches + feat_matches))
            u_l_ids = list(set(u_l_loc_ids + u_l_feat_ids))

            for _, l_id in matches:
                if l_id in u_l_ids:
                    u_l_ids.remove(l_id)

            # update
            for g_id, l_id in matches:
                location, feature = local_msr_info[l_id]["location"], local_msr_info[l_id]["feature"]
                if location:
                    global_msr_info[g_id]["locations"].append(location)
                if feature:
                    global_msr_info[g_id]["features"].extend(feature)
                global_msr_info[g_id]["info"].update(local_msr_info[l_id]["info"])

            # create
            for l_id in u_l_ids:
                g_id = current_global_id
                global_msr_info[g_id] = {"locations": [], "features": [], "info": {}}
                location, feature = local_msr_info[l_id]["location"], local_msr_info[l_id]["feature"]
                if location:
                    global_msr_info[g_id]["locations"].append(location)
                if feature:
                    global_msr_info[g_id]["features"].extend(feature)
                global_msr_info[g_id]["info"].update(local_msr_info[l_id]["info"])
                current_global_id += 1

        # ----- # # -------------------------- #
        # PART-2: Make tracks and update them. #
        # ----- # # -------------------------- #
        trk_loc_ids = [_id for _id in self.tracks.keys() if self.tracks[_id].location]
        msr_loc_ids = [_id for _id in global_msr_info.keys() if global_msr_info[_id]["locations"]]
        trk_feat_ids = [_id for _id in self.tracks.keys() if self.tracks[_id].features]
        msr_feat_ids = [_id for _id in global_msr_info.keys() if global_msr_info[_id]["features"]] 

        if len(trk_loc_ids) and len(msr_loc_ids):
            # compute cost
            trk_locs = np.array([self.tracks[_id]._location for _id in trk_loc_ids])
            msr_locs = np.array([np.array(global_msr_info[_id]["locations"]).mean(0) for _id in msr_loc_ids])
            ccost = euclidean_squared_distance(trk_locs, msr_locs)
            # assingment
            loc_matches, u_trk_loc_ids, u_msr_loc_ids = linear_assignment(ccost, trk_loc_ids, msr_loc_ids, self.trk_inf_loc_cost)
        else:
            loc_matches, u_trk_loc_ids, u_msr_loc_ids = [], trk_loc_ids, msr_loc_ids

        for trk_id, msr_id in loc_matches:
            if trk_id in trk_feat_ids:
                trk_feat_ids.remove(trk_id)
            if msr_id in msr_feat_ids:
                msr_feat_ids.remove(msr_id)

        if len(trk_feat_ids) and len(msr_feat_ids):
            # compute cost
            trk_feats = np.array([np.array(self.tracks[_id].features).mean(0) for _id in trk_feat_ids])
            msr_feats = np.array([np.array(global_msr_info[_id]["features"]).mean(0) for _id in msr_feat_ids])
            ccost = feature_cosine_distance(trk_feats, msr_feats)
            # assingment
            feat_matches, u_trk_feat_ids, u_msr_feat_ids = linear_assignment(ccost, trk_feat_ids, msr_feat_ids, self.trk_inf_feat_cost)
        else:
            feat_matches, u_trk_feat_ids, u_msr_feat_ids = [], trk_feat_ids, msr_feat_ids

        matches = loc_matches + feat_matches
        u_trk_ids = list(set(u_trk_loc_ids + u_trk_feat_ids))
        u_msr_ids = list(set(u_msr_loc_ids + u_msr_feat_ids))

        # update mached tracks and remove them from unmatched tracks and measures
        for trk_id, msr_id in matches:
            self.tracks[trk_id].update(global_msr_info[msr_id])
            if trk_id in u_trk_ids:
                u_trk_ids.remove(trk_id)
            if msr_id in u_msr_ids:
                u_msr_ids.remove(msr_id)

        # missed tracks (unmatched tracks)
        for trk_id in u_trk_ids:
            self.tracks[trk_id].miss()
            if not self.tracks[trk_id].active:
                track = self.tracks.pop(trk_id)
                if track.confirmed:
                    self.deactive_tracks[trk_id] = track
                else:
                    self.list_of_ids.append(trk_id)

        # create new tracks (unmatched measures)
        for msr_id in u_msr_ids:
            trk_id = self.list_of_ids.pop()
            self.tracks[trk_id] = GTrack(trk_id, global_msr_info[msr_id])

        # compute feature matching between unconfirmed tracks and deactive tracks
        uc_feat_trk_ids = [_id for _id in self.tracks.keys() if not self.tracks[_id].confirmed and self.tracks[_id].features]
        d_feat_trk_ids = [_id for _id in self.deactive_tracks.keys() if self.deactive_tracks[_id].features]
        if len(uc_feat_trk_ids) and len(d_feat_trk_ids):
            uc_trk_features = np.array([np.array(self.tracks[_id].features).mean(0) for _id in uc_feat_trk_ids])
            d_trk_features = np.array([np.array(self.deactive_tracks[_id].features).mean(0) for _id in d_feat_trk_ids])
            ccost = feature_cosine_distance(uc_trk_features, d_trk_features)
            # assingment
            matched_ids, _, _ = linear_assignment(ccost, uc_feat_trk_ids, d_feat_trk_ids, self.trk_inf_feat_cost)
            # activate deactive tracks
            for uc_trk_id, d_trk_id in matched_ids:
                self.tracks[d_trk_id] = self.tracks.pop(uc_trk_id)
                self.list_of_ids.append(uc_trk_id)
                d_track = self.deactive_tracks.pop(d_trk_id)
                self.tracks[d_trk_id].id = d_track.id
                self.tracks[d_trk_id].age += d_track.age
                self.tracks[d_trk_id].features.extend(d_track.features)
  
        # kalman predict
        for trk_id in list(self.tracks.keys()):
            if self.tracks[trk_id].active:
                self.tracks[trk_id].location_filter._predict()
