import numpy as np


class PoseGenerator:
    def __init__(self, cfg):
        self.data = np.load(cfg["data"])
        self.n = 0

    def __next__(self):
        fn, pose = self.data[self.n]
        self.n += 1
        return pose
