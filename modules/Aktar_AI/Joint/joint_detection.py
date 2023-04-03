
from .modules.inference_engine_pytorch import InferenceEnginePyTorch
from .modules.parse_poses import parse_poses_2d
import numpy as np
import cv2


class JointDetector(object):
    def __init__(self, cfg):
        self.net = InferenceEnginePyTorch(cfg["weights"], cfg["device"])

    def detect_one(self, img):
        stride = 8
        base_height = 256
        conf_thresh = 5
        input_scale = base_height / img.shape[0]
        scaled_img = cv2.resize(img, dsize=None, fx=input_scale, fy=input_scale)
        scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
        inference_result = self.net.infer(scaled_img)
        poses_2d = parse_poses_2d(inference_result, input_scale, stride, conf_thresh)
        return poses_2d
