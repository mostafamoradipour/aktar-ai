from copy import deepcopy
import numpy as np
import random
import json


with open("walk-data.json", "r") as f:
    walk_data = json.load(f)

with open("standing.json", "r") as f:
    standing = json.load(f)

# person_ids = {0, 1, 2}
# start_locations = np.array([[17, 8], [-15, 15], [1, -7]], dtype="float64")
# stop_locations = np.array([[2, 7], [1, 9], [1, 5]], dtype="float64")

person_ids = {0}
start_locations = np.array([[24, 7]], "float64")
middle_locations = np.array([[3, -5]], "float64")
stop_locations = np.array([[-20, -5]], "float64")

step = 0.15
stoped_ids = set()
list_of_colors = ["%06x" % random.randint(0, 0xFFFFFF) for _ in person_ids]
directions = (middle_locations - start_locations)
directions = directions / np.tile(np.linalg.norm(directions, axis=1).reshape(len(person_ids), 1), (1, 2))
result = []
counter = 0
locations = start_locations

while True:
    data = {"persons": [], "congestions": []}
    data["person_current_count"] = len(person_ids)

    for _id in person_ids:

        person = {}
        person["id"] = _id + 1
        person["location"] = {"x": locations[_id][0], "z": locations[_id][1]}
        person["direction"] = {"x": directions[_id][0], "z": directions[_id][1]}
        person["isFallen"] = False
        person["joints"] = []
        person["best_bodies"] = []
        person["best_faces"] = []
        person["height"] = 170
        person["warning"] = False

        if np.linalg.norm(locations[_id] - middle_locations[_id] < step / 2):
            directions = (stop_locations - middle_locations)
            directions = directions / np.tile(np.linalg.norm(directions, axis=1).reshape(len(person_ids), 1), (1, 2))

        # check if the person is not at the stop location
        if np.linalg.norm(locations[_id] - stop_locations[_id]) > (step / 2):
            pose_id = counter % 8 + 1
            person["pose_id"] = pose_id
            person["bones"] = deepcopy(walk_data[pose_id - 1]["bones"])
            person["isWalking"] = True
            locations[_id] = locations[_id] + step * directions[_id]
        else:
            pose_id = 9
            person["pose_id"] = pose_id
            person["bones"] = deepcopy(standing["bones"])
            person["isWalking"] = False
            stoped_ids.add(_id)

        data["persons"].append(person)

    counter += 1

    result.append(data)

    if stoped_ids == person_ids:
        break


with open("result.json", "w") as f:
    json.dump(result, f)
