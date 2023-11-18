import json


class DataLoader:
    def __init__(self, cfg, step=1):
        self.data = []
        self.num_of_vids = len(cfg.keys())
        for key in cfg.keys():
            with open(cfg[key], "r") as f:
                self.data.append(json.load(f))
        self.n = 0
        self.step = step

    def __next__(self):
        record = []
        for cam_idx in range(self.num_of_vids):
            record.append(self.data[cam_idx][self.n])
        self.n += self.step
        return record
