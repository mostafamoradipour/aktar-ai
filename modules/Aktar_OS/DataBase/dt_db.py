from pymongo import MongoClient


class DTdatabase():
    def __init__(self, cfg):
        host = cfg['host']
        port = int(cfg['port'])
        client = MongoClient(host, port)
        self.collection = client[cfg['database']][cfg['collection']]

    def update_dt(self, dt_doc):
        cur = self.collection.find({'id': dt_doc['id']})
        if len(list(cur)):
            self.collection.update_one({'id': dt_doc['id']}, {'$push': {
                'location_history': dt_doc['location']
                }})
            record = {'height': dt_doc['height']}
            update = {"$set": record}
            self.collection.update_one({'id': dt_doc['id']}, update)
        else:
            self.collection.insert_one({'id': dt_doc['id'], 'height': dt_doc['height'], 'location_history': [dt_doc['location']]})
