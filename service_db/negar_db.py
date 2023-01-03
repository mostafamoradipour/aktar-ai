from glob import glob
import pymongo
import base64
import cv2


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
# username = "beautysalon4132"
username = "alr.akbari"
collection = db[username]


# documents = collection.find()
# for doc in documents:
#         print(doc)


def read_b64_img(img_pth):
        img = cv2.imread(img_pth)
        _, im_arr = cv2.imencode('.jpg', img)  # im_arr: image in Numpy one-dim array format.
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode()
        return im_b64


# for count in range(4):
#         data = {"name": f"cam_{count}", "url": "http..."}
#         collection.update_one({'doc_id':'camera_streams'},{'$push': {'images':data}}, upsert=True)

# pths = glob("imgs/*")
# for count, pth in enumerate(pths):
#         im_b64 = read_b64_img(pth)
#         record = {'id': count, 'face': im_b64, 'appearance': im_b64}
#         collection.update_one({'doc_id':'customer_data'},{'$push': {'images':record}}, upsert=True)


collection.delete_many({'doc_id':'customer_data'})
# collection.insert_one({'doc_id':'camera_streams', 'cameras':[
#                                         {"name": "cam_1", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_2", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=2&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_3", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=2&stream=1.sdp?real_stream--rtp-caching=800"},
#                                         {"name": "cam_4", "url": "rtsp://2.181.225.8:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800"}]
#                                         })

documents = collection.find()
for doc in documents:
        print(doc)
