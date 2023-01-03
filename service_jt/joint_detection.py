
from .modules.inference_engine_pytorch import InferenceEnginePyTorch
from .modules.parse_poses import parse_poses
from .modules.draw import draw_poses
import numpy as np
import json
import time
import cv2
import os


class JointDetector(object):
    def __init__(self, cfg):
        self.net = InferenceEnginePyTorch(cfg["weights"], cfg["device"])

    def detect_one(self, img):
        stride = 8
        base_height = 512
        input_scale = base_height / img.shape[0]
        scaled_img = cv2.resize(img, dsize=None, fx=input_scale, fy=input_scale)
        scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
        fx = np.float32(0.8 * img.shape[1])
        inference_result = self.net.infer(scaled_img)
        poses_3d, poses_2d = parse_poses(inference_result, input_scale, stride, fx)
        draw_poses(img, poses_2d)
        if len(poses_2d):
            poses_2d = poses_2d[:, :-1].reshape(-1, 19, 3)[:, :, :2]
            poses_2d = np.concatenate((poses_2d[:, :2, :], poses_2d[:, 3:]), axis=1)
        return poses_2d, img
