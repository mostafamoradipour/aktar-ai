from confluent_kafka import Producer
import json
import yaml

from modules.Aktar_AI.Pose.pose_estimation import PoseEstimator
from modules.Aktar_AI.DTwin.dt_engine import DTEngine
from modules.Aktar_C.streaming import StreamerV1


def main():
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg["dt"]

    estimator = PoseEstimator(cfg['pose_estimation'])
    engine = DTEngine(cfg["engine"])
    vid1 = StreamerV1(cfg["stream"][0], max_queue_size=10)
    vid2 = StreamerV1(cfg["stream"][1], max_queue_size=10)
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
    vid2.thread.start()
    while True:
        ret1, frame1 = vid1.read_last()
        ret2, frame2 = vid2.read_last()
        if ret1 and ret2:
            frames = [frame1, frame2]
            num_cams = len(frames)
            all_cams_poses = estimator(frames)
            result = engine.step(frames, num_cams, all_cams_poses)
            if len(result["persons"]):
                producer.produce(topic, json.dumps(result), 'data', callback=delivery_callback)
        else:
            break

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()
    # Release cameras
    vid1.release()
    vid2.release()


if __name__ == "__main__":
    main()
