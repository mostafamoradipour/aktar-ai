from pymongo import MongoClient
from queue import Queue
import numpy as np
import base64
import cv2


class Database():
    def __init__(self, cfg):
        host = cfg['host']
        port = int(cfg['port'])
        client = MongoClient(host, port)
        self.collection = client[cfg['database']][cfg['collection']]
        self.queue_size = cfg['queue_maxsize']

    def load_feature(self):
        features = dict()
        faces = []
        ids = []
        areas = []
        aspect_ratioes = []
        time_stamps = []
        documents = self.collection.find()
        id_counter = 0
        try:
            for index, doc in enumerate(documents):
                q = Queue(maxsize = self.queue_size)
                q.put((np.array(doc['feature'])))
                features[index] = q
                faces.append(np.array(doc['face_']))
                ids.append(doc['id'])
                areas.append(doc['area'])
                aspect_ratioes.append(doc['aspect_ratio'])
                time_stamps.append(doc['time'])

            id_counter = max([i['id'] for i in self.collection.find()]) + 1    
        except:
            pass
        return ids, areas, aspect_ratioes, features, faces, time_stamps, id_counter

    def save_feature(self, face, norm_feat, face_, area, aspect_ratio, id, time_stamp):
        _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()

        # _, face_arr = cv2.imencode('.jpg', face_) 
        # face_bytes = face_arr.tobytes()
        # face_b64 = base64.b64encode(face_bytes).decode()


        record = {'id': id,
                  'face': im_b64,
                  'face_': face.tolist(),
                  'feature': norm_feat.tolist(),
                  'area': area,
                  'aspect_ratio': aspect_ratio,
                  'time': time_stamp}
        self.collection.insert_one(record)

    def update_feature(self, face, norm_feat, face_, area, aspect_ratio, id, time_stamp):
        _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()

        # _, face_arr = cv2.imencode('.jpg', face_) 
        # face_bytes = face_arr.tobytes()
        # face_b64 = base64.b64encode(face_bytes).decode()


        record = {'id': id,
                  'face': im_b64,
                  'face_': face.tolist(),
                  'feature': norm_feat.tolist(),
                  'area': area,
                  'aspect_ratio': aspect_ratio,
                  'time': time_stamp}

        filter = {'id': id}
        update = { "$set": record}
        self.collection.update_one(filter, update)
    
    def update_time(self, id, time_stamp):
        
        record = {'id': id,
                  'time': time_stamp}

        filter = {'id': id}
        update = { "$set": record}
        self.collection.update_one(filter, update)

    def get_docs(self):
        docs = []
        documents = self.collection.find()
        for doc in documents:
            del doc["_id"]
            docs.append(doc)
        return docs


if __name__ == "__main__":
    cfg = {
    "host": "0.0.0.0",
    "port": 27017,
    "database": "Aktar",
    "collection": "CDM"
    }
    db = Database(cfg)
    samples = db.get_docs()
    print(samples)
