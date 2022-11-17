from pymongo import MongoClient
import numpy as np
import base64
import cv2
from queue import Queue

class Database():
    def __init__(self, cfg):
        host = cfg['host']
        port = int(cfg['port'])
        client = MongoClient(host, port)
        self.collection = client[cfg['database']][cfg['collection']]
        self.queue_size = cfg['queue_maxsize']

    def load_feature(self):
        body_features = dict()
        faces = []
        ids = []
        body_areas = []
        body_aspect_ratioes = []
        face_areas = []
        face_aspect_ratioes = []
        time_stamps = []
        body_counters = []
        face_counters = []
        documents = self.collection.find()
        id_counter = 0
        try:
            for index, doc in enumerate(documents):
                q = Queue(maxsize = self.queue_size)
                q.put((np.array(doc['body_feature'])))
                body_features[index] = q
                body_counters.append(doc['body_counter'])
                face_counters.append(doc['face_counter'])
                face_areas.append(doc['face_area'])
                face_aspect_ratioes.append(doc['face_aspect_ratio'])
                faces.append(np.array(doc['best_face']))
                ids.append(doc['id'])
                body_areas.append(doc['body_area'])
                body_aspect_ratioes.append(doc['body_aspect_ratio'])
                time_stamps.append(doc['time'])

            id_counter = max([i['id'] for i in self.collection.find()]) + 1    
        except:
            pass
        face_att = faces, face_counters, face_areas, face_aspect_ratioes
        body_att = body_features, body_counters, body_areas, body_aspect_ratioes
        return ids, body_att, face_att, time_stamps, id_counter

    def save_feature(self, body, body_norm_feat, body_area, body_aspect_ratio,  face, face_counter, face_area, face_aspect_ratio, id, time_stamp):
        _, im_arr = cv2.imencode('.jpg', body)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()

        record = {'id': id,
                  'best_body': im_b64,
                  'best_body_1': im_b64,
                  'body_counter': 1,
                  'best_face': face.tolist(),
                  'best_face_1': face.tolist(),
                  'face_counter': face_counter,
                  'body_feature': body_norm_feat.tolist(),
                  'body_area': body_area,
                  'body_aspect_ratio': body_aspect_ratio,
                  'face_area': face_area,
                  'face_aspect_ratio': face_aspect_ratio,
                  'time': time_stamp}
        self.collection.insert_one(record)

    def update_body_feature(self, body, body_counter, body_norm_feat, body_area, body_aspect_ratio, id, time_stamp, method = None):
        _, im_arr = cv2.imencode('.jpg', body)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()

        record = {'id': id,
                  'best_body': im_b64,
                  f'best_body_{body_counter}': im_b64,
                  'body_counter': body_counter,
                  'body_feature': body_norm_feat.tolist(),
                  'body_area': body_area,
                  'body_aspect_ratio': body_aspect_ratio,\
                  'time': time_stamp}

        if method == 'save':
            self.collection.insert_one(record)

        else:
            filter = {'id': id}
            update = { "$set": record}
            self.collection.update_one(filter, update)

    def update_face(self, face, face_counter, face_area, face_aspect_ratio, id):
        if face.shape[0] > 1:
            _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes).decode()

            record = {'best_face': im_b64,
                      f'best_face_{face_counter}': im_b64,
                      'face_counter': face_counter,
                      'face_area': face_area,
                      'face_aspect_ratio': face_aspect_ratio}
        
        else:
            record = {'best_face': None,
                      'face_counter': face_counter,
                      'face_area': face_area,
                      'face_aspect_ratio': face_aspect_ratio}

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
