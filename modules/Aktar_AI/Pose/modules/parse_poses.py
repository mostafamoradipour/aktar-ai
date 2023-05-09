import numpy as np

from .pose import Pose, propagate_ids
try:
    from pose_extractor import extract_poses
except:
    print('#### Cannot load fast pose extraction, switched to legacy slow implementation. ####')
    from .legacy_pose_extractor import extract_poses

AVG_PERSON_HEIGHT = 180

# pelvis (body center) is missing, id == 2
map_id_to_panoptic = [1, 0, 9, 10, 11, 3, 4, 5, 12, 13, 14, 6, 7, 8, 15, 16, 17, 18]

limbs = [[18, 17, 1],
         [16, 15, 1],
         [5, 4, 3],
         [8, 7, 6],
         [11, 10, 9],
         [14, 13, 12]]


def get_root_relative_poses(inference_results):
    heatmap, paf_map = inference_results

    upsample_ratio = 4
    found_poses = extract_poses(heatmap[0:-1], paf_map, upsample_ratio)[0]
    # scale coordinates to features space
    found_poses[:, 0:-1:3] /= upsample_ratio
    found_poses[:, 1:-1:3] /= upsample_ratio

    poses_2d = []
    num_kpt_panoptic = 19
    num_kpt = 18
    for pose_id in range(found_poses.shape[0]):
        if found_poses[pose_id, 3] == -1:  # skip pose if does not found neck
            continue
        pose_2d = np.ones(num_kpt_panoptic * 3 + 1, dtype=np.float32) * -1  # +1 for pose confidence
        for kpt_id in range(num_kpt):
            if found_poses[pose_id, kpt_id * 3] != -1:
                x_2d, y_2d = found_poses[pose_id, kpt_id * 3:kpt_id * 3 + 2]
                conf = found_poses[pose_id, kpt_id * 3 + 2]
                pose_2d[map_id_to_panoptic[kpt_id] * 3] = x_2d  # just repacking
                pose_2d[map_id_to_panoptic[kpt_id] * 3 + 1] = y_2d
                pose_2d[map_id_to_panoptic[kpt_id] * 3 + 2] = conf
        pose_2d[-1] = found_poses[pose_id, -1]
        poses_2d.append(pose_2d)

    return np.array(poses_2d)


previous_poses_2d = []


def parse_poses(inference_results, input_scale, stride, fx):
    is_video = True
    global previous_poses_2d
    poses_3d, poses_2d, features_shape = get_root_relative_poses(inference_results)
    poses_2d_scaled = []
    for pose_2d in poses_2d:
        num_kpt = (pose_2d.shape[0] - 1) // 3
        pose_2d_scaled = np.ones(pose_2d.shape[0], dtype=np.float32) * -1  # +1 for pose confidence
        for kpt_id in range(num_kpt):
            if pose_2d[kpt_id * 3] != -1:
                pose_2d_scaled[kpt_id * 3] = int(pose_2d[kpt_id * 3] * stride / input_scale)
                pose_2d_scaled[kpt_id * 3 + 1] = int(pose_2d[kpt_id * 3 + 1] * stride / input_scale)
                pose_2d_scaled[kpt_id * 3 + 2] = pose_2d[kpt_id * 3 + 2]
        pose_2d_scaled[-1] = pose_2d[-1]
        poses_2d_scaled.append(pose_2d_scaled)

    if is_video:  # track poses ids
        current_poses_2d = []
        for pose_id in range(len(poses_2d_scaled)):
            pose_keypoints = np.ones((Pose.num_kpts, 2), dtype=np.int32) * -1
            for kpt_id in range(Pose.num_kpts):
                if poses_2d_scaled[pose_id][kpt_id * 3] != -1.0:  # keypoint was found
                    pose_keypoints[kpt_id, 0] = int(poses_2d_scaled[pose_id][kpt_id * 3 + 0])
                    pose_keypoints[kpt_id, 1] = int(poses_2d_scaled[pose_id][kpt_id * 3 + 1])
            pose = Pose(pose_keypoints, poses_2d_scaled[pose_id][-1])
            current_poses_2d.append(pose)
        propagate_ids(previous_poses_2d, current_poses_2d)
        previous_poses_2d = current_poses_2d

    translated_poses_3d = []
    # translate poses
    for pose_id in range(len(poses_3d)):
        pose_3d = poses_3d[pose_id].reshape((-1, 4)).transpose()
        pose_2d = poses_2d[pose_id][:-1].reshape((-1, 3)).transpose()
        num_valid = np.count_nonzero(pose_2d[2] != -1)
        pose_3d_valid = np.zeros((3, num_valid), dtype=np.float32)
        pose_2d_valid = np.zeros((2, num_valid), dtype=np.float32)
        valid_id = 0
        for kpt_id in range(pose_3d.shape[1]):
            if pose_2d[2, kpt_id] == -1:
                continue
            pose_3d_valid[:, valid_id] = pose_3d[0:3, kpt_id]
            pose_2d_valid[:, valid_id] = pose_2d[0:2, kpt_id]
            valid_id += 1

        pose_2d_valid[0] = pose_2d_valid[0] - features_shape[2]/2
        pose_2d_valid[1] = pose_2d_valid[1] - features_shape[1]/2
        mean_3d = np.expand_dims(pose_3d_valid.mean(axis=1), axis=1)
        mean_2d = np.expand_dims(pose_2d_valid.mean(axis=1), axis=1)
        numerator = np.trace(np.dot((pose_3d_valid[:2, :] - mean_3d[:2, :]).transpose(),
                                    pose_3d_valid[:2, :] - mean_3d[:2, :])).sum()
        numerator = np.sqrt(numerator)
        denominator = np.sqrt(np.trace(np.dot((pose_2d_valid[:2, :] - mean_2d[:2, :]).transpose(),
                                              pose_2d_valid[:2, :] - mean_2d[:2, :])).sum())
        mean_2d = np.array([mean_2d[0, 0], mean_2d[1, 0], fx * input_scale / stride])
        mean_3d = np.array([mean_3d[0, 0], mean_3d[1, 0], 0])
        translation = numerator / denominator * mean_2d - mean_3d

        if is_video:
            translation = current_poses_2d[pose_id].filter(translation)
        for kpt_id in range(19):
            pose_3d[0, kpt_id] = pose_3d[0, kpt_id] + translation[0]
            pose_3d[1, kpt_id] = pose_3d[1, kpt_id] + translation[1]
            pose_3d[2, kpt_id] = pose_3d[2, kpt_id] + translation[2]
        translated_poses_3d.append(pose_3d.transpose().reshape(-1))

    return np.array(translated_poses_3d), np.array(poses_2d_scaled)


def parse_poses_2d(inference_results, input_scale, stride, conf_thresh=5):
    poses_2d = get_root_relative_poses(inference_results)
    poses = []
    for pose_2d in poses_2d:
        # if pose_2d[-1] < conf_thresh:
        #     continue
        num_kpt = (pose_2d.shape[0] - 1) // 3
        pose_2d_scaled = np.ones(pose_2d.shape[0], dtype=np.float32) * -1  # +1 for pose confidence
        for kpt_id in range(num_kpt):
            if pose_2d[kpt_id * 3] != -1:
                pose_2d_scaled[kpt_id * 3] = int(pose_2d[kpt_id * 3] * stride / input_scale)
                pose_2d_scaled[kpt_id * 3 + 1] = int(pose_2d[kpt_id * 3 + 1] * stride / input_scale)
                pose_2d_scaled[kpt_id * 3 + 2] = pose_2d[kpt_id * 3 + 2]
        pose_2d_scaled[-1] = pose_2d[-1]
        # pose = pose_2d_scaled[:-1].reshape(19, 3)[:, :2]
        poses.append(pose_2d_scaled)
    return  np.array(poses)
