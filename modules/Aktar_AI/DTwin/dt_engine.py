from copy import deepcopy
import numpy as np
import json

from modules.Aktar_AI.DTwin.utils.utils import euclidean_squared_distance2, linear_assignment, match_by_location
from modules.Aktar_AI.DTwin.mapping import PointMapper
from modules.Aktar_AI.DTwin.track import Track


class DTEngine():
    def __init__(self, cfg):
        with open(cfg['pose_data'], 'r') as f:
            self.pose_data = json.load(f)
        self.mapper = PointMapper(cfg['mapping'])
        self.tracks = {}
        self.missed_tracks = {}
        self.fallen_tracks = {}
        self.list_of_ids = list(range(1000, 0, -1))
        self.congestion_map = np.zeros((20, 20), dtype="float") # for a 10 by 10 square meter place, resolution: 1 meter, stride = 0.5 meter

    def step(self, all_cams_poses):

        num_cams = len(all_cams_poses)
        all_tracks = {track.id: np.array(track.location_filter.x[:2]).reshape(2) for track in self.tracks.values()}
        all_m_trk_ids = set()
        
        # define current frame congestion map
        congestion_map = np.zeros((20, 20), dtype="float")

        for cam_id in range(num_cams):

            tracks = {track.id: track.poses[cam_id] for track in self.tracks.values() if cam_id in track.poses.keys()}
            poses = all_cams_poses[cam_id]
            # poses = remove_too_close_poses(poses)

            est_ids = list(range(len(poses)))
            trk_ids = list(tracks.keys())                

            if len(est_ids) and len(trk_ids):
                prev_poses = np.array(list(tracks.values()))
                ccost = euclidean_squared_distance2(prev_poses, poses)            
                matches, _, u_est_ids = linear_assignment(ccost, trk_ids, est_ids)
            elif not len(est_ids) and not len(trk_ids):
                continue
            else:
                matches, _, u_est_ids = [], trk_ids, est_ids

            '''
                find location and height for new estimations, match by location and make a new track
                or update the matched track.
            '''
            for est_id in u_est_ids:
                pose = poses[est_id]
                simplified_pose = self.simplify_pose(pose)
                neck, _, ankle = simplified_pose
                posture = self.process_pose(simplified_pose)
                ms_location = self.mapper.map(cam_id, ankle) if ankle else None
                if not ms_location:
                    continue

                ms_height = self.mapper.height(cam_id, ms_location, neck) if neck and posture == "stand" else None
                all_trks_ids, all_trks_locs = list(all_tracks.keys()), list(all_tracks.values())
                mached_idx = match_by_location(all_trks_locs, ms_location)

                if mached_idx >= 0:
                    trk_id = all_trks_ids[mached_idx]
                    self.tracks[trk_id].update(cam_id, pose, ms_location, ms_height)
                else:
                    trk_id = self.list_of_ids.pop()
                    self.tracks[trk_id] = Track(trk_id, cam_id, pose, ms_location, ms_height)

            '''
                find location and height for new estimations of matched tracks and update them.
            '''
            for trk_id, est_id in matches:

                # pose extraction and analysis
                pose = poses[est_id]
                simplified_pose = self.simplify_pose(pose)
                neck, hip, ankle = simplified_pose
                posture = self.process_pose(simplified_pose)

                track = self.tracks[trk_id]

                if posture == "fall":
                    # fall measurements
                    fall_location = self.mapper.map(cam_id, hip)
                    fall_location = {"x": fall_location[0] / 100, "z": fall_location[1] / 100}
                    if ankle:
                        x, z = self.mapper.map(cam_id, ankle)
                        fall_direction = {"x": fall_location[0] - x, "z": fall_location[1] - z}
                    elif neck:
                        x, z = self.mapper.map(cam_id, neck)
                        fall_direction = {"x": x - fall_location[0], "z": z - fall_location[1]}
                    track.fall(cam_id, pose, fall_location, fall_direction)
                    
                else:
                    # standing measurements
                    # location measurement
                    ms_location = self.mapper.map(cam_id, ankle) if ankle else None
                    if not ms_location:
                        continue

                    # measure height 
                    ms_height = self.mapper.height(cam_id, ms_location, neck) if ms_location and neck and posture == "stand" else None

                    # update the matched track
                    track.update(cam_id, pose, ms_location, ms_height)

                # update set of matched track ids
                all_m_trk_ids.add(trk_id)

        # for trk_id, track in self.fallen_tracks.copy().items():
        #     if time() - track.fall_time > 10:
        #         self.missed_tracks[trk_id] = track
        #         self.fallen_tracks.pop(trk_id)

        for trk_id, track in self.tracks.copy().items():
            # tracks that are not matched with any detection
            if track.id not in all_m_trk_ids:
                self.tracks[trk_id].missed()
            
            if not track.active:
                if track.confirmed:
                    self.missed_tracks[trk_id] = track
                else:
                    self.list_of_ids.append(trk_id)
                self.tracks.pop(trk_id)

            elif track.isFallen:
                if track.confirmed:
                    self.fallen_tracks[trk_id] = track
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
                        congestion_map[x - 1, z - 1 ] += 0.5
                        congestion_map[x - 1, z] += 0.5
                        congestion_map[x, z - 1] += 0.5
                    elif z <= 0:
                        congestion_map[x - 1, z] += 0.5
                    elif x <= 0:
                        congestion_map[x, z - 1] += 0.5

                    if z < 9 and x < 9:
                        congestion_map[x + 1, z + 1 ] += 0.5
                        congestion_map[x + 1, z] += 0.5
                        congestion_map[x, z + 1] += 0.5
                    elif z >= 9:
                        congestion_map[x + 1, z] += 0.5
                    elif x >= 9:
                        congestion_map[x, z + 1] += 0.5

        # overal congestion map update
        congestion_map[congestion_map < 1] = 0.0
        self.congestion_map = congestion_map  + self.congestion_map -5 * np.array(congestion_map == 0) * np.array(self.congestion_map >= 5)

        # Prepare result for UI
        # result = {"persons": [], "fallens": [], "congestions": []}
        result = {"persons": [], "congestions": []}

        # find congestion locations
        cong_locs = np.where(self.congestion_map > 25)
        # add congestions
        for idx in range(len(cong_locs[0])):
            x = float(cong_locs[0][idx]) * 0.5 + 0.25
            z = float(cong_locs[1][idx]) * 0.5 + 0.25
            congestion = {"x": x, "z": z}
            result["congestions"].append(congestion)

        # add active persons
        for track in self.tracks.values():
            if not track.confirmed:
                continue
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["isFallen"] = track.isFallen
            data["isWalking"] = track.isWalking
            data["joints"] = [] if track.isWalking else self.extract_bones(track.poses[1 if 1 in track.poses.keys() else 0])
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = True if self.zone(track.location) == 1 else False
            result["persons"].append(data)

        # add fallen persons
        for track in self.fallen_tracks.values():
            data = deepcopy(self.pose_data)[track.pose_id]
            data["id"] = track.id
            data["isFallen"] = track.isFallen
            data["isWalking"] = track.isWalking
            data["joints"] = []
            data["location"] = track.location
            data["direction"] = track.direction
            data["height"] = track.height
            data["warning"] = True if self.zone(track.location) == 1 else False
            result["persons"].append(data)

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
