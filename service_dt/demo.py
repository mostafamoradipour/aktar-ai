from time import sleep
import numpy as np
import json


class locEngine_demo():
    def __init__(self):
        with open('service_dt/walk-data.json', 'r') as f:
            self.walking_model = json.load(f)
        self.locs = np.arange(0, 6.35, 0.1)

    def find(self):
        pose_id = 0
        loc_id = 0
        while True:
            sleep(0.1)
            if pose_id > 7:
                pose_id = 0
            data = self.walking_model[pose_id]
            if loc_id > len(self.locs) - 1:
                loc_id = 0
            z = self.locs[loc_id]
            x = 3
            if z > 5:
                data["fallen"] = True
            else:
                data["fallen"] = False
            data["location"] = {"x": x+2.5, "z": z-0.5}
            pose_id += 1
            loc_id += 1
            yield [data]
