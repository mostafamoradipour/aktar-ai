
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
        file_path = os.path.join('service_jt/data', 'extrinsics.json')
        with open(file_path, 'r') as f:
            extrinsics = json.load(f)
        R = np.array(extrinsics['R'], dtype=np.float32)
        t = np.array(extrinsics['t'], dtype=np.float32)
        base_height = 128
        input_scale = base_height / img.shape[0]
        scaled_img = cv2.resize(img, dsize=None, fx=input_scale, fy=input_scale)
        scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
        fx = np.float32(0.8 * img.shape[1])
        t0 = time.time()
        inference_result = self.net.infer(scaled_img)
        # print('Infer: {:1.3f}'.format(time.time()-t0))
        t0 = time.time()
        poses_3d, poses_2d = parse_poses(inference_result, input_scale, stride, fx)
        # print('Extract: {:1.3f}'.format(time.time()-t0))
        draw_poses(img, poses_2d)
        if len(poses_2d):
            poses_2d = poses_2d[:, :-1].reshape(-1, 19, 3)[:, :, :2]
            poses_2d = np.concatenate((poses_2d[:, :2, :], poses_2d[:, 3:]), axis=1)
        return poses_2d, img
