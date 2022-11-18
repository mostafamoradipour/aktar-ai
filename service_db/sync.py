import requests


def sync_negar(cam_col, cdm_col, email):
    cam_url = 'https://api.kachrobotics.com/api/user/post_camera_stream/'
    cdm_url = 'https://api.kachrobotics.com/api/user/customer_data/'
    res = requests.delete(url=cdm_url, json={"email": email})
    if res.status_code == 200:
        print("Negar CDM deleted!")
    g_c = {}  # general counter
    while True:
        cameras = cam_col.get_docs()
        persons = cdm_col.get_docs()
        public_cameras = []
        for camera in cameras:
            del camera["play"]
            public_ip = requests.get('https://api.ipify.org').text
            local_ip = camera["url"].split("://")[1].split(":554")[0]
            camera["url"] = camera["url"].replace(local_ip, public_ip)
            public_cameras.append(camera)
        res = requests.post(url=cam_url, json={
                            "email": email, "cameras": public_cameras})
        print("camera", res.status_code)
        public_persons = []
        for person in persons:
            _id = person["id"]
            if _id not in g_c.keys():
                g_c[_id] = {"face": 0, "body": 0, "time": 0}
            faces = [person[f"best_face_{count+1}"] for count in range(person["face_counter"])]
            bodies = [person[f"best_body_{count+1}"] for count in range(person["body_counter"])]
            times = person["time"]
            if len(faces) > g_c[_id]["face"] or len(bodies) > g_c[_id]["body"] or len(times) > g_c[_id]["time"]:
                faces = [person[f"best_face_{count+1}"] for count in range(person["face_counter"])]
                public_person = {"id": _id, "faces": faces[g_c[_id]["face"]:],
                                "bodies": bodies[g_c[_id]["body"]:], "times": times[g_c[_id]["time"]:]}
                g_c[_id]["face"] += len(faces)
                g_c[_id]["body"] += len(bodies)
                g_c[_id]["time"] += len(times)
                public_persons.append(public_person)
        if len(public_persons):
            while True:
                record =  {"email": email, "persons": public_persons}
                print(record)
                res = requests.post(url=cdm_url, json=record)
                if res.status_code == 200:
                    print("CDM", res.status_code)
                    break


if __name__ == "__main__":
    sync_negar()
