# General utils
from pathlib import Path
import numpy as np
import logging
import math
import cv2
import os


# Settings
np.set_printoptions(linewidth=320, formatter={'float_kind': '{:11.5g}'.format})  # format short g, %precision=5
cv2.setNumThreads(0)  # prevent OpenCV from multithreading (incompatible with PyTorch DataLoader)
os.environ['NUMEXPR_MAX_THREADS'] = str(min(os.cpu_count(), 8))  # NumExpr max threads


def set_logging(rank=-1):
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO if rank in [-1, 0] else logging.WARN)


def check_requirements(file='requirements.txt'):
    # Check installed dependencies meet requirements
    import pkg_resources
    requirements = pkg_resources.parse_requirements(Path(file).open())
    requirements = [x.name + ''.join(*x.specs) if len(x.specs) else x.name for x in requirements]
    pkg_resources.require(requirements)  # DistributionNotFound or VersionConflict exception if requirements not met


def check_img_size(img_size, s=32):
    # Verify img_size is a multiple of stride s
    new_size = make_divisible(img_size, int(s))  # ceil gs-multiple
    if new_size != img_size:
        print('WARNING: --img-size %g must be multiple of max stride %g, updating to %g' % (img_size, s, new_size))
    return new_size


def make_divisible(x, divisor):
    # Returns x evenly divisible by divisor
    return math.ceil(x / divisor) * divisor


def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def xywhn2xyxy(x, w=640, h=640, padw=32, padh=32):
    # Convert nx4 boxes from [x, y, w, h] normalized to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = w * (x[:, 0] - x[:, 2] / 2) + padw  # top left x
    y[:, 1] = h * (x[:, 1] - x[:, 3] / 2) + padh  # top left y
    y[:, 2] = w * (x[:, 0] + x[:, 2] / 2) + padw  # bottom right x
    y[:, 3] = h * (x[:, 1] + x[:, 3] / 2) + padh  # bottom right y
    return y


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clip(0, img_shape[1])  # x1
    boxes[:, 1].clip(0, img_shape[0])  # y1
    boxes[:, 2].clip(0, img_shape[1])  # x2
    boxes[:, 3].clip(0, img_shape[0])  # y2


def NMS(dets, scores, thresh): 
    """Pure Python NMS baseline."""
    #X1, Y1, X2, Y2, and score assignment 
    x1 = dets[:, 0] 
    y1 = dets[:, 1] 
    x2 = dets[:, 2] 
    y2 = dets[:, 3] 
    #Area of each detection frame 
    areas = (x2 - x1 + 1) * (y2 - y1 + 1) 
    #Sort in descending order of score confidence 
    order = scores.argsort()[::-1] 
    Keep = [] # reserved result box set 
    while order.size > 0: 
        i = order[0]
        Keep.append(i)
        # keep. The highest score of the remaining APPI # box # is reserved 
        #Get the intersection area, top left and bottom right 
        xx1 = np.maximum(x1[i], x1[order[1:]]) 
        yy1 = np.maximum(y1[i], y1[order[1:]]) 
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]]) 
        #Calculate the area of intersection. When there is no overlap, the area is 0 
        w = np.maximum(0.0, xx2 - xx1 + 1) 
        h = np.maximum(0.0, yy2 - yy1 + 1) 
        inter = w * h 
        #Calculate IOU: overlapping area / (area 1 + area 2 - overlapping area) 
        ovr = inter / (areas[i] + areas[order[1:]] - inter) 
        #Retain boxes with IOU less than the threshold 
        inds = np.where(ovr <= thresh)[0] 
        order = order [inds + 1] # because the length of ovr array is one less than that of order array, all subscripts should be moved back one bit 
    return Keep


def non_max_suppression_person(prediction, conf_thres=0.25, iou_thres=0.45, agnostic=True, max_det=1000, nm=0,):
    """Runs Non-Maximum Suppression (NMS) on inference results

    Returns:
         list of detections, on (n, 16) tensor per image [xyxy, conf, landmarks, cls]
    """
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

    # Settings
    min_wh, max_wh = 2, 4096  # (pixels) minimum and maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    mi = 5 + nc  # mask start index
    # output = [np.zeros((0, 16))] * prediction.shape[0]
    output = [np.zeros((0, 6 + nm))] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])
        mask = x[:, mi:] 

        # Detections matrix nx6 (xyxy, conf, cls)
        conf = np.amax(x[:,5:], 1).reshape(-1, 1)
        j = np.argmax(x[:,5:], 1).reshape(-1, 1)
        x_1 = np.concatenate((box, conf, x[:, 5:], j), 1)[conf.ravel() > conf_thres]
        x = np.concatenate((box, conf, j, mask), 1)[conf.ravel() > conf_thres]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = NMS(boxes, scores, iou_thres)  # NMS

        if len(i) > max_det:  # limit detections
            i = i[:max_det]
            #Filter by class --> Person's class number = 0
        if len(i)>0:
            filtered_class =  x[i, -1]== 0 
            output[xi] = x[i][filtered_class]
        else:
            print('not found any person')

    return output
 