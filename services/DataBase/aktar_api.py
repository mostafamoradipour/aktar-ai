from pymongo import MongoClient
import logging
logger = logging.getLogger(__name__)
# logger.propagate = False
logger.info("Hello from database api module")


class apiDB():
    def __init__(self, cfg):
        client = MongoClient(cfg["host"], cfg["port"])
        self.collection = client[cfg["database"]][cfg["collection"]]

    def add_cam(self, camera):
        self.collection.insert_one(camera)

    def remove_cam(self, name):
        self.collection.delete_many({"name": name})

    def reset(self):
        self.collection.drop()

    def get_docs(self):
        docs = []
        # documents = self.collection.find({"id": {"$gt": last_id}})
        documents = self.collection.find()
        for doc in documents:
            del doc["_id"]
            docs.append(doc)
        return docs
