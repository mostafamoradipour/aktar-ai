import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np
import json
import yaml

from mapping import PointMapper


with open('demo/map_cfg.yaml', 'r') as f:
    cfg = yaml.safe_load(f)


with open('demo/ankle_tracks_123.json', 'r') as f:
    ankle_track = json.load(f)
print(len(ankle_track))

cam_idx = 1
point_mapper = PointMapper(cfg)


position_track = []

for idx, (time, ankle) in enumerate(ankle_track):
    if idx < 93 or idx > 435:
        continue
    location = point_mapper.map(cam_idx, ankle)
    position_track.append([time, location])

with open("demo/postion_track_123.json", 'w') as f:
    json.dump(position_track, f)

import pdb; pdb.set_trace()
