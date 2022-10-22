from pymongo import MongoClient
import numpy as np
import base64
import cv2


class Database():
    def __init__(self, cfg):
        host = cfg['host']
        port = int(cfg['port'])
        client = MongoClient(host, port)
        self.collection = client[cfg['database']][cfg['collection']]

    def load_feature(self):
        samples = []
        documents = self.collection.find()
        self.id_counter = 0
        try:
            for index, doc in enumerate(documents):
                samples.append(np.array(doc['feature']))
            samples = np.array(samples)    
            self.id_counter = max([i['id'] for i in self.collection.find()])      
        except:
            pass
        return samples

    def save_feature(self, face, norm_feat):
        _, im_arr = cv2.imencode('.jpg', face)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()
        self.id_counter += 1
        record = {'id': self.id_counter,
                  'face': im_b64,
                  'feature': norm_feat.tolist()}
        self.collection.insert_one(record)

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
