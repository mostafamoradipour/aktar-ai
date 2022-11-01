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
        samples = dict()
        ids = []
        areas = []
        documents = self.collection.find()
        id_counter = 0
        try:
            for index, doc in enumerate(documents):
                # samples.append(np.array(doc['feature']))
                q = Queue(maxsize = self.queue_size)
                q.put((np.array(doc['feature'])))
                samples[index] = q
                ids.append(doc['id'])
                areas.append(doc['area'])

            # ids = np.array(ids)
            # areas = np.array(areas) 
            # samples = np.array(samples) 

            id_counter = max([i['id'] for i in self.collection.find()]) + 1    
        except:
            pass
        return ids, areas, samples, id_counter

    def save_feature(self, face, norm_feat, area, id):
        _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()
        record = {'id': id,
                  'face': im_b64,
                  'feature': norm_feat.tolist(),
                  'area': area}
        self.collection.insert_one(record)

    def update_feature(self, face, norm_feat, area, id):
        _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()
        record = {'id': id,
                  'face': im_b64,
                  'feature': norm_feat.tolist(),
                  'area': area}

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
