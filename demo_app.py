from confluent_kafka import Producer
from time import sleep
from tqdm import tqdm
import json
import yaml

from modules.Aktar_AI.Pose.demo_pose_estimation import PoseGenerator
from modules.Aktar_AI.DTwin.demo_dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1


def main1():
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg["dt"]

    pose_generator = PoseGenerator(cfg['demo_pose_estimation'])
    engine = DTEngine(cfg["engine"])
    vid1 = StreamerV1(cfg["stream"][0], max_queue_size=10, frame_skip=4)
    # Create Producer instance
    producer = Producer(cfg["kafka"]["server"])
    topic = cfg["kafka"]["topic"]


    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


    vid1.thread.start()

    while True:
        ret1, frame1 = vid1.read_last()

        if ret1:
            frames = [frame1]
            num_cams = len(frames)
            all_cams_poses = pose_generator.next()
            result = engine.step(frames, num_cams, all_cams_poses)
            if len(result["persons"]):
                producer.produce(topic, json.dumps(result), 'data', callback=delivery_callback)
        else:
            break
    
    # Release cameras
    vid1.release()

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()


def main():
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
        sleep(0.2)

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()


if __name__ == "__main__":
    main()
