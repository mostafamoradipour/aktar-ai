from database.api_db import Database


db = Database()

camera = {
    "name": "cam_1",
    "url": "rtsp://..."
}

db.add_cam(camera)
cameras = db.load_cameras()
print(cameras[0])
