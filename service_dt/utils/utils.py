from service_af.verification.detection.person_detection import PersonDetector
from service_cs.streaming import StreamerV1
import numpy as np
import json


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


class locEngine_box():
    def __init__(self, cfg, url):
        with open('service_dt/walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.detector = PersonDetector(cfg)
        self.url = url

    def find(self):
        pose_id = 0
        vid = StreamerV1(self.url)
        x, z = 0, 0
        while True:
            ret, frame = vid.read_last()
            if pose_id > 7:
                pose_id = 0
            data = self.walking_model[pose_id]
            _, boxes = self.detector.detect_one(frame, None)
            if boxes:
                x, z = find_distance_angle_box(boxes[0])
                z = z + 1.25
                x  = x + 2.5
            data["location"] = {"x": x+2.5, "z": z-0.5}
            pose_id += 1
            yield [data]


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
