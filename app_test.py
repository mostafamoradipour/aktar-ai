from confluent_kafka import Producer
from time import sleep
from tqdm import tqdm
from time import time
import numpy as np
import json
import yaml
import cv2

from aktarai.recognition import BodyFeatureExtractor
from aktarai.detection import PersonDetector
from aktarai.tracking import GTracker

# from aktarai.recognition import DataLoader
# from aktarai.detection import DataLoader


def main(user="mostafa", funcs={"detection": 1, "recognition": 1}, show=False):
    with open("config-test.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]

    if "detection" in funcs.keys():
        if funcs["detection"]:
            person_detector = PersonDetector(cfg["detection"])
        else:
            person_detector = DetectionDataLoader(cfg["detection"])

    if "recognition" in funcs.keys():
        if funcs["recognition"]:
            body_feature_extractor = BodyFeatureExtractor(cfg["recognition"])
        else:
            body_feature_extractor = ExtractionDataLoader(cfg["recognition"])

    if "tracking" in funcs.keys():
        person_tracker = GTracker(cfg["tracking"])

    vids = []
    for idx in cfg["video"].keys():
        vids.append(cv2.VideoCapture(cfg["video"][idx]))

    # Create Producer instance
    producer = Producer(cfg["kafka"]["server"])
    topic = cfg["kafka"]["topic"]


    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))


    frame_count = 0
    data = []
    while True:
        result = {}

        start_time = time()
        frames = []
        for vid in vids:
            ret, frame = vid.read()
            if not ret:
                break
            frames.append(frame)

        frame_count += 1
        if frame_count % 2 != 0:
            continue

        if frame_count > 4500:
            break

        if ret:
            if "detection" in funcs.keys():
                result["detection"] = person_detector(frames)
            if "recognition" in funcs.keys():
                result["recognition"] = body_feature_extractor(frames, result["detection"])
            if "tracking" in funcs.keys():
                result["tracking"] = person_tracker.step(frames, result)
                if len(result["tracking"]["persons"]):
                    producer.produce(topic, json.dumps(result["tracking"]), 'data', callback=delivery_callback)

            # data.append(result["tracking"])

        else:
            break

        sleep(0.05)
        print(f"FPS: {round(1 / (time()-start_time))}")

    # Release videos
    for vid in vids:
        vid.release()

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()

    with open(cfg["result"], "w") as f:
        json.dump(data, f)


def type1(user="mostafa"):
    with open("config-test.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]

    dataloader = DataLoader(cfg['pose_estimation'])

    person_tracker = GTracker(cfg["tracking"])

    vids = []
    for idx in range(dataloader.num_of_vids):
        vids.append(cv2.VideoCapture(cfg["video"][idx]))

    # Create Producer instance
    producer = Producer(cfg["kafka"]["server"])
    topic = cfg["kafka"]["topic"]


    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        # else:
        #     print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
        #         topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    frame_count = 0

    data = []

    while True:
        start_time = time()
        frames = []
        for vid in vids:
            ret, frame = vid.read()
            if not ret:
                break
            frames.append(frame)

        if ret:
            all_cams_persons = next(dataloader)
            frame_count += 1

            if frame_count % 2 != 0:
                continue

            if frame_count > 4500:
                break

            result = person_tracker.step(frames, all_cams_persons)

            if len(result["persons"]):
                producer.produce(topic, json.dumps(result), 'data', callback=delivery_callback)

            data.append(result)

        else:
            break

        sleep(0.06)
        print(f"FPS: {round(1 / (time()-start_time))}")

    # Release videos
    for vid in vids:
        vid.release()

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()

    with open(cfg["result"], "w") as f:
        json.dump(data, f)


def type2(user="mostafa"):
    with open("config-test.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]

    with open(cfg["result"], 'r') as f:
        dt = json.load(f)

    # Create Producer instance
    producer = Producer(cfg["kafka"]["server"])
    topic = cfg["kafka"]["topic"]


    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


    for data in tqdm(dt):
        producer.produce(topic, json.dumps(data), 'data', callback=delivery_callback)
        sleep(0.1)

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()


def process_videos(user="mostafa"):
    with open("config-test.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter("out.avi", fourcc, 12.0, (480, 540))

    vids = []
    for idx in range(0, 2, 1):
        vids.append(cv2.VideoCapture(cfg["video"][idx]))

    frame_count = 0

    while True:
        start_time = time()
        frames = []
        for vid in vids:
            ret, frame = vid.read()
            if not ret:
                break
            frame = cv2.resize(frame, (480, 270))
            frames.append(frame)

        if ret:

            frame_count += 1

            # if frame_count <= 250:
            #     continue

            # if frame_count > 1250:
            #     break

            # out_frame = np.concatenate((np.concatenate(frames[:2]), np.concatenate(frames[2:])), axis=1)
            out_frame = np.concatenate((frames[0], frames[1]), axis=0)
            # print(out_frame.shape)
            # out_frame = frame
            out.write(out_frame)
            print(frame_count)
        else:
            break

    # Release videos
    for vid in vids:
        vid.release()
    out.release()


if __name__ == "__main__":
    main(user="mostafa")


'''
import matplotlib.pyplot as plt
from collections import deque

def type1():

    # This code is for movement index plots

    fig, ax = plt.subplots()
    bar_colors = ['tab:red', 'tab:blue', 'tab:orange']
    rects = ax.bar([1, 2, 3], [600, 600, 600], label=[1, 2, 3], color=bar_colors)
    for rect in rects:
        rect.set_height(0)


    # Create a fixed-length deque of size 50 to store the data points
    data_points = deque(maxlen=1000)
    # Create an empty plot
    fig, ax = plt.subplots()
    line = ax.plot([])
    # Set the x-axis and y-axis limits to 100
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 2000)

    while True:
        if ret:
            if frame_count % 18 == 0:
                if len(result["persons"]):
                    ids, movements = [], []
                    for person in result["persons"]:
                        ids.append(int(person["id"]))
                        movements.append(person["movement"])
                    ids = np.argsort(ids)
                    # movements = sorted(movements, key=lambda index: ids[index], reverse=True)
                    for idx, rect in enumerate(rects[:len(movements)]):
                        rect.set_height(movements[ids[idx]])
                    fig.canvas.draw()
                    plt.pause(0.0001)

            if frame_count % 2 == 0:
                persons = result["persons"]
                if len(persons):
                    # Generate and add data points to the deque
                    data_points.append((frame_count, persons[0]["movement"]))
                
                    # Update the plot with the new data points
                    x_values = [x for x, y in data_points]
                    y_values = [y for x, y in data_points]
                    line[0].set_data(x_values, y_values)
                    # pause the plot for 0.01s before next point is shown
                    plt.pause(0.001)
'''
