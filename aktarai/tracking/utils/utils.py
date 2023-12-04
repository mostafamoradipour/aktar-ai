from scipy.optimize import linear_sum_assignment
from cv2 import boundingRect
from copy import deepcopy
import numpy as np
import cv2


INF_COST = 100 


def get_box_from_pose(pose):
    x1 = max(0, int(pose[:, 0].min()))
    y1 = max(0, int(pose[:, 1].min()))
    x2 = max(0, int(pose[:, 0].max()))
    y2 = max(0, int(pose[:, 1].max()))
    return x1, y1, x2, y2


def find_distance_angle_box(tlbr):
    camera_alpha = 80 * np.pi / 180
    camera_beta = 45 * np.pi / 180
    camera_height = 0.8
    img_height = 1080
    img_width = 1920
    # camera_angle = 0 * np.pi / 180
    w = tlbr[2] - tlbr[0]
    point_x = tlbr[2] - w / 2
    point_y = tlbr[3]
    alpha = (point_x - img_width / 2) / img_width * camera_alpha
    beta = (point_y - img_height / 2) / img_height * camera_beta 
    z = camera_height * np.tan(np.pi / 2 - beta)
    x = -1 * z * np.tan(alpha)
    return x, z


def find_distance_angle_joint(loc_i):
    camera_alpha = 80 * np.pi / 180
    camera_beta = 45 * np.pi / 180
    camera_height = 0.8
    img_height = 1080
    img_width = 1920
    # camera_angle = 0 * np.pi / 180
    point_x = loc_i[0]
    point_y = loc_i[1]
    alpha = (point_x - img_width / 2) / img_width * camera_alpha
    beta = (point_y - img_height / 2) / img_height * camera_beta 
    z = camera_height * np.tan(np.pi / 2 - beta)
    x = -1 * z * np.tan(alpha)
    return x, z


def feature_cosine_distance(input1, input2):
    input1 = input1 / np.linalg.norm(input1, axis=1).reshape(-1, 1)
    input2 = input2 / np.linalg.norm(input2, axis=1).reshape(-1, 1)
    dismat = (1 - input1 @ input2.T) / 2
    return dismat


def feature_euclidean_squared_distance(input1, input2):
    input1 = input1 / np.linalg.norm(input1, axis=1)
    input2 = input2 / np.linalg.norm(input2, axis=1)
    m, n = input1.shape[0], input2.shape[0]
    distmat = np.tile(np.power(input1, 2).sum(axis=1, keepdims=True), (1, n)) + \
            np.tile(np.power(input2, 2).sum(axis=1, keepdims=True), (1, m)).T
    distmat = distmat -2 * input1 @ input2.T
    return distmat


def euclidean_squared_distance(input1, input2):
    """Computes euclidean squared distance.

    Args:
        input1 (numpy.array): 2-D poses matrix.
        input2 (numpy.array): 2-D poses matrix.

    Returns:
        numpy.array: distance matrix.
    """
    m, n = input1.shape[0], input2.shape[0]
    distmat = np.tile(np.power(input1, 2).sum(axis=1, keepdims=True), (1, n)) + \
            np.tile(np.power(input2, 2).sum(axis=1, keepdims=True), (1, m)).T
    distmat = distmat -2 * input1 @ input2.T
    return distmat


def euclidean_squared_distance2(input1, input2):
    """Computes euclidean squared distance.

    Args:
        input1 (numpy.array): 2-D poses matrix.
        input2 (numpy.array): 2-D poses matrix.

    Returns:
        numpy.array: distance matrix.
    """
    m, n = input1.shape[0], input2.shape[0]
    distmat = np.zeros((m, n))
    input1 = input1.reshape(-1, 19*2)
    input2 = input2.reshape(-1, 19*2)
    for i, inp1 in enumerate(input1):
        for j, inp2 in enumerate(input2):
            mask = np.array(inp1 > 0) * np.array(inp2 > 0)
            inp1_masked, inp2_masked = inp1[mask], inp2[mask]
            distmat[i, j] = np.linalg.norm(inp2_masked - inp1_masked) / len(inp1_masked)
    return distmat


def cosine_distance(input1, input2):
    """Computes cosine distance.

    Args:
        input1 (numpy.array): 2-D poses matrix.
        input2 (numpy.array): 2-D poses matrix.

    Returns:
        numpy.array: distance matrix.
    """
    norm_input1 = input1 / np.norm(input1, axis=1)
    norm_input2 = input2 / np.norm(input2, axis=1)
    distmat = norm_input1 @ norm_input2.T
    return distmat


def linear_assignment(cost, row_ids, col_ids, inf_cost):
    """Solves the linear assignment problem.
    Parameters
    ----------
    cost : ndarray
        The cost matrix.
    row_ids : List[int]
        IDs that correspond to each row in the cost matrix.
    col_ids : List[int]
        IDs that correspond to each column in the cost matrix.
    Returns
    -------
    List[tuple], List[int], List[int]
        Matched row and column IDs, unmatched row IDs, and unmatched column IDs.
    """
    cost = cost.clip(0, inf_cost)
    m_rows, m_cols = linear_sum_assignment(cost)
    row_ids = np.fromiter(row_ids, int, len(row_ids))
    col_ids = np.fromiter(col_ids, int, len(col_ids))
    return _get_assignment_matches(cost, row_ids, col_ids, m_rows, m_cols, inf_cost)


def _get_assignment_matches(cost, row_ids, col_ids, m_rows, m_cols, inf_cost):
    unmatched_rows = list(set(range(cost.shape[0])) - set(m_rows))
    unmatched_cols = list(set(range(cost.shape[1])) - set(m_cols))
    unmatched_row_ids = [row_ids[row] for row in unmatched_rows]
    unmatched_col_ids = [col_ids[col] for col in unmatched_cols]
    matches = []
    for row, col in zip(m_rows, m_cols):
        if cost[row, col] < inf_cost:
            matches.append((row_ids[row], col_ids[col]))
        else:
            unmatched_row_ids.append(row_ids[row])
            unmatched_col_ids.append(col_ids[col])
    return matches, unmatched_row_ids, unmatched_col_ids


def match_by_location(locs, loc):
    if len(locs):
        locs = np.array(locs).reshape(-1, 2)
        loc = np.array(loc).reshape(-1, 2)
        dists =  np.linalg.norm(locs - loc, axis=1)
        if dists.min() < INF_COST:
            return dists.argmin()
    return -1


def get_bodies1(image, boxes, poses):
    if not len(boxes):
        return None, None
    # extract bodies
    bodies = [image[y1: y2, x1: x2, :] for (x1, y1, x2, y2) in boxes]
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # ar: area, as: aspect ratio
    bodies_ar_as = np.array([((y2 - y1) * (x2 - x1), (y2 - y1) / (x2 - x1)) for (x1, y1, x2, y2) in boxes])
    bodies_ar, bodies_as = bodies_ar_as[:, 0:1], bodies_ar_as[:, 1:]
    # in: intensity
    bodies_in = np.array([[hsv_img[y1: y2, x1: x2, 2].sum()] for (x1, y1, x2, y2) in boxes]) / bodies_ar
    bodies_scores = np.concatenate((bodies_in, bodies_ar, bodies_as), axis=1)
    return bodies, bodies_scores


def get_bodies(image, poses):
    if not len(poses):
        return None, None
    body_boxes = np.array([boundingRect(pose[(pose[:, 0] > 0) * (pose[:, 1] > 0)]) for pose in poses])
    # body box refinement
    h, w = image.shape[:2]
    x1s = np.clip(body_boxes[:, 0:1] - body_boxes[:, 2:3] // 10, 0, w)
    y1s = np.clip(body_boxes[:, 1:2] - body_boxes[:, 3:4] // 5, 0, h)
    x2s = np.clip(body_boxes[:, 0:1] + body_boxes[:, 2:3] + body_boxes[:, 2:3] // 10, 0, w)
    y2s = np.clip(body_boxes[:, 1:2] + body_boxes[:, 3:4] + body_boxes[:, 3:4] // 10, 0, h)
    body_boxes = np.concatenate((x1s, y1s, x2s, y2s), axis=1)
    # extract bodies
    bodies = [image[y1: y2, x1: x2, :] for (x1, y1, x2, y2) in body_boxes]
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # ar: area, as: aspect ratio
    bodies_ar_as = np.array([((y2 - y1) * (x2 - x1), (y2 - y1) / (x2 - x1)) for (x1, y1, x2, y2) in body_boxes])
    bodies_ar, bodies_as = bodies_ar_as[:, 0], bodies_ar_as[:, 1]
    # in: intensity
    bodies_in = np.array([hsv_img[y1: y2, x1: x2, 2].sum() for (x1, y1, x2, y2) in body_boxes]) / bodies_ar
    body_scores = (bodies_in, bodies_ar, bodies_as)
    return bodies, body_scores


def get_faces(image, poses):
    if not len(poses):
        return None, None, None
    if len(poses[0]) == 17:
        poses = poses[:, :5]
    else:
        poses = np.concatenate((poses[:, 0:2, :], poses[:, 15:, :]), axis=1) # keypoints related to face
    face_exist = [(pose > 0).all() for pose in poses]
    face_boxes = np.array([boundingRect(pose) for pose in poses])
    # face box refinement
    h, w = image.shape[:2]
    x1s = np.clip(face_boxes[:, 0:1] - face_boxes[:, 2:3] // 10, 0, w)
    y1s = np.clip(face_boxes[:, 1:2] - face_boxes[:, 3:4] // 2, 0, h)
    x2s = np.clip(face_boxes[:, 0:1] + face_boxes[:, 2:3] + face_boxes[:, 2:3] // 10, 0, w)
    y2s = np.clip(face_boxes[:, 1:2] + face_boxes[:, 3:4] + face_boxes[:, 3:4] // 10, 0, h)
    face_boxes = np.concatenate((x1s, y1s, x2s, y2s), axis=1)
    # extract faces
    faces = [image[y1: y2, x1: x2, :] for (x1, y1, x2, y2) in face_boxes]
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # ar: area, as: aspect ratio
    faces_ar_as = np.array([((y2 - y1) * (x2 - x1), (y2 - y1) / (x2 - x1)) for (x1, y1, x2, y2) in face_boxes])
    faces_ar, faces_as = faces_ar_as[:, 0], faces_ar_as[:, 1]
    # in: intensity
    faces_in = np.array([hsv_img[y1: y2, x1: x2, 2].sum() for (x1, y1, x2, y2) in face_boxes]) / faces_ar
    face_scores = (faces_in, faces_ar, faces_as)
    return faces, face_scores, face_exist
