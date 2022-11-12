from time import sleep
import requests


def sync_negar(cam_col, cdm_col, email):
    cam_url = 'https://api.kachrobotics.com/api/user/post_camera_stream/'
    cdm_url = 'https://api.kachrobotics.com/api/user/customer_data/'
    count = 0
    while True:
        cameras = cam_col.get_docs()
        persons = cdm_col.get_docs()
        public_cameras = []
        for camera in cameras:
            del camera["play"]
            ip = requests.get('https://api.ipify.org').text
            camera["url"] = camera["url"].replace("192.168.1.102", ip)
            public_cameras.append(camera)
        res = requests.post(url=cam_url, json={"cameras": public_cameras, "email": email})
        print("camera", res.status_code)
        public_persons = []
        for person in persons[count:]:
            del person["feature"]
            person["appearance"] = person["face"]
            public_persons.append(person)
        if len(public_persons):
            res = requests.post(url=cdm_url, json={"images": public_persons, "email": email})
            print("CDM", res.status_code)
        if res.status_code == 200:
            count = len(persons)
        sleep(1)


if __name__=="__main__":
    sync_negar()
