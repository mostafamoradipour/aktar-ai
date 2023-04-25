import numpy as np


def get_confidence(queue_features, norm_feat):
    '''
        geting max confidence for a peron's queue 
    '''
    queue_size = queue_features.qsize()
    if queue_size > 0:
        features = [queue_features.queue[i] for i in range(queue_size)]
        features = np.array(features)
        confs = (1 + (features @ norm_feat)).reshape(-1)
    else:
        return 0
    return confs.max()


def body_face_assign(body_boxes, face_boxes):
    """
    From SORT: Computes IOU between two bboxes in the form [x1,y1,x2,y2]
    """
    body_boxes = np.expand_dims(body_boxes, 0)
    face_boxes = np.expand_dims(face_boxes, 1)
    xx1 = np.maximum(face_boxes[..., 0], body_boxes[..., 0])
    yy1 = np.maximum(face_boxes[..., 1], body_boxes[..., 1])
    xx2 = np.minimum(face_boxes[..., 2], body_boxes[..., 2])
    yy2 = np.minimum(face_boxes[..., 3], body_boxes[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    out = wh / ((face_boxes[..., 2] - face_boxes[..., 0]) * (face_boxes[..., 3] - face_boxes[..., 1])
                + (body_boxes[..., 2] - body_boxes[..., 0]) * (body_boxes[..., 3] - body_boxes[..., 1]) - wh)
    return out


def linear_assignment(cost_matrix):
    # try:
    #     import lap
    #     _, x, y = lap.lapjv(cost_matrix, extend_cost=True)
    #     return np.array([[y[i], i] for i in x if i >= 0])
    # except ImportError:
    from scipy.optimize import linear_sum_assignment
    x, y = linear_sum_assignment(cost_matrix)
    return np.array(list(zip(x, y)))
