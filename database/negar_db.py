import pymongo


db_uri = 'mongodb://185.231.59.241:27017/'
db_name = 'chaw2022'
db_username = 'chaw'
password = 'chaw2022'
auth = 'admin'
mechanism = 'SCRAM-SHA-1'


client = pymongo.MongoClient(
        db_uri,
        username=db_username,
        password=password,
        authSource=auth,
        authMechanism=mechanism )

db = client[db_name]
collection  = db["mostafa.moradipoor73"]
documents = collection.find()
for doc in documents:
        print(doc)

# collection.delete_many({'doc_id':'camera_streams'})


# collection.insert_one({'doc_id':'camera_streams', 'cameras':[
#                                         {"name": "cam_1", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_2", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=2&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_3", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=2&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_4", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800"}]
#                                         })
