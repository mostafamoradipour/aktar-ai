
from .modules.inference_engine_pytorch import InferenceEnginePyTorch
from .modules.parse_poses import parse_poses_2d
import numpy as np
import cv2


class PoseEstimator(object):
    def __init__(self, cfg):
        self.net = InferenceEnginePyTorch(cfg["weights"], cfg["device"])

    def __call__(self, imgs):
        stride = 8
        base_height = 256
        conf_thresh = 5
        scaled_imgs = []
        for img in imgs:
            input_scale = base_height / img.shape[1]
            scaled_img = cv2.resize(img, dsize=None, fx=input_scale, fy=input_scale)
            scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
            scaled_imgs.append(scaled_img)
        inference_results = self.net.infer(scaled_imgs)
        poses = []
        for idx in range(len(inference_results[0])):
            result = (inference_results[0][idx], inference_results[1][idx])
            poses_2d = parse_poses_2d(result, input_scale, stride, conf_thresh)
            poses.append(poses_2d)
        return poses
