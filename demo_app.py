from confluent_kafka import Producer
import matplotlib.pyplot as plt
from collections import deque
from time import sleep
from tqdm import tqdm
from time import time
import numpy as np
import json
import yaml
import cv2

from modules.Aktar_AI.Pose.demo_pose import PoseGenerator
from modules.Aktar_AI.DTwin.demo_dt import DTEngine


def type1():
    with open('config-demo1.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg["dt"]

    pose_generator = PoseGenerator(cfg['pose_estimation'])

    engine = DTEngine(cfg["engine"])
    
    vids = []
    for idx in range(pose_generator.num_of_vids):
        vids.append(cv2.VideoCapture(cfg["video"][idx]))

    # Create Producer instance
    producer = Producer(cfg["kafka"]["server"])
    topic = cfg["kafka"]["topic"]


    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    frame_count = 0


    # fig, ax = plt.subplots()
    # bar_colors = ['tab:red', 'tab:blue', 'tab:orange']
    # rects = ax.bar([1, 2, 3], [600, 600, 600], label=[1, 2, 3], color=bar_colors)
    # for rect in rects:
    #     rect.set_height(0)


    # Create a fixed-length deque of size 50 to store the data points
    data_points = deque(maxlen=1000)
    # Create an empty plot
    fig, ax = plt.subplots()
    line = ax.plot([])
    # Set the x-axis and y-axis limits to 100
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 2000)


    while True:
        start_time = time()
        frames = []
        for vid in vids:
            ret, frame = vid.read()
            if not ret:
                break
            frames.append(frame)

        if ret:
            all_cams_poses = next(pose_generator)
            frame_count += 1

            if frame_count % 2 != 0:
                continue

            if frame_count > 4500:
                break

            result = engine.step(frames, all_cams_poses)

            # if frame_count % 18 == 0:
            #     if len(result["persons"]):
            #         ids, movements = [], []
            #         for person in result["persons"]:
            #             ids.append(int(person["id"]))
            #             movements.append(person["movement"])
            #         ids = np.argsort(ids)
            #         # movements = sorted(movements, key=lambda index: ids[index], reverse=True)
            #         for idx, rect in enumerate(rects[:len(movements)]):
            #             rect.set_height(movements[ids[idx]])
            #         fig.canvas.draw()
            #         plt.pause(0.0001)
            

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


            # if len(result["persons"]):
                # producer.produce(topic, json.dumps(result), 'data', callback=delivery_callback)

        else:
            break
        
        sleep(0.03)
        print(f"FPS: {round(1 / (time()-start_time))}")

    plt.show()
    # Release cameras
    for vid in vids:
        vid.release()

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()


def type2():
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg["dt"]

    with open(cfg["demo_data"], 'r') as f:
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


def process_videos():
    with open('config-demo.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg["dt"]

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter("out.avi", fourcc, 25.0, (960, 540))

    vids = []
    for idx in range(0, 4, 1):
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

            if frame_count <= 250:
                continue

            if frame_count > 1250:
                break

            out_frame = np.concatenate((np.concatenate(frames[:2]), np.concatenate(frames[2:])), axis=1)
            # out_frame = frame
            out.write(out_frame)
            
            print(frame_count)
        else:
            break

    # Release cameras
    for vid in vids:
        vid.release()
    out.release()


if __name__ == "__main__":
    type1()
