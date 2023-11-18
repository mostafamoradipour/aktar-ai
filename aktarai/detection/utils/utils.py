import numpy as np


def yolov8pose_post_process(detections, threshold=0.75):
    result = []
    for res in detections:
        bconfs = res.boxes.conf
        boxes = res.boxes.xyxy.reshape(-1, 4)[bconfs > threshold]
        boxes = boxes.cpu().numpy().astype("int32")
        keypoints = res.keypoints.xy.reshape(-1, 17, 2)[bconfs > threshold]
        keypoints = keypoints.cpu().numpy().astype("int32")
        if res.keypoints.conf != None:
            confs = res.keypoints.conf[bconfs > threshold]
            confs = confs.cpu().numpy().reshape(-1, 17)
        else:
            confs = np.array([]).reshape(-1, 17).astype("float32")
        result.append({"boxes": boxes, "keypoints": keypoints, "confs": confs})
    return result


def extract_bodies(image, boxes):
    result = [image[box[1]: box[3], box[0]: box[2], :] for box in boxes]
    return result


def is_suitable_for_track(boxes):
    ar = boxes[:, 0:1]

def is_suitable_for_track(boxes):
    if boxes.ndim == 1:
        result = True if boxes[0] else False
    else:
        result = [is_suitable_for_track(box) for box in boxes]
    return result
