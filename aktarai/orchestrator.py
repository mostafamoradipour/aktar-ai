from confluent_kafka import Producer
from time import sleep
from tqdm import tqdm
from time import time
import numpy as np
import random
import json
import cv2

from aktarai.recognition import BodyFeatureExtractor
from aktarai.detection import PersonDetector
from aktarai.streaming import StreamerV1
from aktarai.tracking import GTracker2


random.seed(0)


class Orchestrator(object):
    def __init__(self, cfg):
        self.save = cfg["orchestration"]["save"]
        self.funcs = cfg["orchestration"]
        self.warning_zones = cfg['warning_zones']
        self.total_congestion_map = np.zeros((40, 40))
        self.list_of_colors = ["%06x" % random.randint(0, 0xFFFFFF) for _ in range(1000)]

        if "detection" in self.funcs.keys():
            if self.funcs["detection"]:
                self.person_detector = PersonDetector(cfg["detection"])
            else:
                self.person_detector = DetectionDataLoader(cfg["detection"])

        if "recognition" in self.funcs.keys():
            if self.funcs["recognition"]:
                self.body_feature_extractor = BodyFeatureExtractor(cfg["recognition"])
            else:
                self.body_feature_extractor = ExtractionDataLoader(cfg["recognition"])

        if "tracking" in self.funcs.keys():
            self.person_tracker = GTracker2(cfg["tracking"])

        self.streams = []
        for idx in cfg["stream"].keys():
            self.streams.append(StreamerV1(cfg["stream"][idx], frame_skip=0, max_queue_size=0))

        # Create Producer instance
        self.kafka_produce = cfg["kafka"]["produce"]
        if self.kafka_produce:
            self.producer = Producer(cfg["kafka"]["server"])
            self.topic = cfg["kafka"]["topic"]

    def delivery_callback(self, err, msg):
        if err:
            print("ERROR: Message failed delivery: {}".format(err))

    def run(self):
        frame_number = 1
        for stream in self.streams:
            stream.thread.start()

        while True:
            result = {}
            start_time = time()
            frames = []
            for stream in self.streams:
                fn = -1
                while fn != frame_number:
                    ret, fn, frame = stream.read_frame()
                if not ret:
                    break
                frames.append(frame)
            if not ret:
                break
            frame_number += 2

            if "detection" in self.funcs.keys():
                result["detection"] = self.person_detector(frames)
            if "recognition" in self.funcs.keys():
                result["recognition"] = self.body_feature_extractor(frames, result["detection"])
            if "tracking" in self.funcs.keys():
                self.person_tracker.step(frames, result["detection"], result["recognition"])

            # prepare result for UI.
            data = {"persons": [], "congestions": [], "person_current_count": 0}

            # add confirmed persons and update congestion map
            self.congestion_map = np.zeros((40, 40))
            for track in self.person_tracker.tracks.values():
                if not track.confirmed:
                    continue
                
                self.update_congestion_map(track.location_filter.x[:2])

                data["person_current_count"] += 1
                # person = deepcopy(self.pose_data)[track.pose_id]
                person = {}
                person["id"] = track.id
                person["color"] = self.list_of_colors[track.id]
                person["best_bodies"] = track.good_bodies.popleft() if len(track.good_bodies) else []
                person["best_faces"] = []
                person["isFallen"] = track.isFallen
                person["isWalking"] = track.isWalking
                person["joints"] = []
                person["location"] = track.location
                person["direction"] = track.direction
                person["height"] = track.height
                person["warning"] = self.warning_check(track.location)
                person["movement_index"] = np.linalg.norm(list(track.direction.values()))
                data["persons"].append(person)

            # total congestion map update
            self.congestion_map[self.congestion_map < 1] = 0.0
            self.total_congestion_map = self.congestion_map  + self.total_congestion_map -5 * np.array(self.congestion_map == 0) * np.array(self.total_congestion_map >= 5)

            # find congestion locations
            cong_locs = np.where(self.total_congestion_map > 25)

            # add congestions
            for idx in range(len(cong_locs[0])):
                x = float(cong_locs[0][idx]) * 0.5 + 0.25
                z = float(cong_locs[1][idx]) * 0.5 + 0.25
                congestion = {"x": x, "z": z}
                data["congestions"].append(congestion)

            if self.kafka_produce:
                self.producer.produce(self.topic, json.dumps(data), "data", callback=self.delivery_callback)

            duration = time() - start_time
            sleep(max(0, 1/6 - duration))
            print(f"FPS: {round(1 / (time() - start_time))}")

        if self.save:
            with open("results/data.json", "w") as f:
                json.dump(data, f)

        # Block until the messages are sent.
        if self.kafka_produce:
            self.producer.poll(10000)
            self.producer.flush()

        # Release cameras
        for stream in self.streams:
            stream.release()

    def warning_check(self, location):
        x, z = location.values()
        for key in self.warning_zones:
            warning_zone = self.warning_zones[key]
            x1, z1, x2, z2 = warning_zone.values()
            if x > x1 and x < x2 and z > z1 and z < z2:
                return True
        return False

    def update_congestion_map(self, location):
        x, z = location // 50
        x, z = int(x), int(z)
        self.congestion_map[x, z] += 0.5
        if z > 0 and x > 0:
            self.congestion_map[x - 1, z - 1] += 0.5
            self.congestion_map[x - 1, z] += 0.5
            self.congestion_map[x, z - 1] += 0.5
        elif z <= 0:
            self.congestion_map[x - 1, z] += 0.5
        elif x <= 0:
            self.congestion_map[x, z - 1] += 0.5

        if z < 9 and x < 9:
            self.congestion_map[x + 1, z + 1] += 0.5
            self.congestion_map[x + 1, z] += 0.5
            self.congestion_map[x, z + 1] += 0.5
        elif z >= 9:
            self.congestion_map[x + 1, z] += 0.5
        elif x >= 9:
            self.congestion_map[x, z + 1] += 0.5
