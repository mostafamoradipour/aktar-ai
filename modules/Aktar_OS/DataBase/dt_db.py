from pymongo import MongoClient


class DTdatabase():
    def __init__(self, cfg):
        host = cfg['host']
        port = int(cfg['port'])
        client = MongoClient(host, port)
        self.collection = client[cfg['db_name']][cfg['username']]

    def update_persons(self, dt_doc):
        cur = self.collection.find({'doc_id':'customer_data', 'persons.id': dt_doc['id']})
        results = list(cur)
        if len(results):
            self.collection.update_one({'doc_id':'customer_data', 'persons.id': dt_doc['id']},{'$push': {
            # 'persons.$.best_faces': { '$each': dt_doc['best_faces'] },
            'persons.$.best_bodies': { '$each': dt_doc['best_bodies'] },
            'persons.$.trajectory': { '$each': [dt_doc['location']] },
            }, '$set': {'persons.$.height': dt_doc['height'] 
            }})
        else:
            dt_doc_new = {'id':dt_doc['id'], 'trajectory':[dt_doc['location']], 'height': dt_doc['height'], 'best_bodies': dt_doc['best_bodies']}
            self.collection.update_one({'doc_id':'customer_data'},{'$push': {'persons': dt_doc_new}}, upsert=True)

    def update_count(self, current_count):
        cur = self.collection.find({'doc_id': 'customer_data'})
        result = list(cur)
        if len(result):
            self.collection.update_one({'doc_id': 'customer_data'}, {'$set': {'person_current_count': current_count}})
        else:
            self.collection.update_one({'doc_id': 'customer_data'}, {'$push': {'person_current_count': current_count}}, upsert=True)
