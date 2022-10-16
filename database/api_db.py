from pymongo import MongoClient


class Database():
    def __init__(self, cfg):
        client = MongoClient(cfg["host"], cfg["port"])
        self.collection = client[cfg["database"]][cfg["collection"]]

    def add_cam(self, camera):
        self.collection.insert_one(camera)

    def remove_cam(self, name):
        self.collection.delete_many({"name": name})

    def get_docs(self):
        docs = []
        documents = self.collection.find()
        for doc in documents:
            del doc["_id"]
            docs.append(doc)
        return docs


if __name__ == "__main__":
    import yaml
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    cdm_col = Database(cfg["database"], "CDM")
    persons = cdm_col.get_docs() # persons = [{"id": 1, "face": base64}, ...]
    # print({"persons": persons})
