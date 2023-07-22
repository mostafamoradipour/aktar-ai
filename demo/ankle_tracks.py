from time import time
import numpy as np
import pickle
import json
import cv2


with open('demo/all_frames_poses.pickle', 'rb') as handle:
    all_frames_poses = pickle.load(handle)
cam_numbers = len(all_frames_poses[0])
colors = [(255, 255, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]

vid = cv2.VideoCapture("../Mapping/data/parand/parand_123.avi")
cam_idx = 1
frame_skip = 0

tracks = []
frame_number = 0

while True:

    # frame read
    ret, frame = vid.read()
    frame_number += 1
    if frame_number % (frame_skip + 1) != frame_skip:
        continue
    
    # process if ret (there is a frame)
    if ret:

        # extract poses
        all_cams_poses = all_frames_poses[frame_number]
        poses = all_cams_poses[cam_idx]
        t = time()

        for pose in poses:

            # apply confidence threshold
            conf = pose[-1]
            if conf < 5:
                continue
            
            # find the ankle
            pose = pose[:-1].reshape(-1, 3)[:, :2]
            if (pose[8] > 0).all() and (pose[14] > 0).all():
                ankle = ((pose[8] + pose[14]) / 2).astype("int").tolist()
            elif (pose[8] > 0).all():
                ankle = pose[8].astype("int").tolist()
            elif (pose[14] > 0).all():
                ankle = pose[14].astype("int").tolist()
            else:
                ankle = None
            
            # tracking
            dists = []
            if ankle:
                for track in tracks:
                    dists.append(np.linalg.norm(np.array(track[-1][1]) - ankle))
                dists = np.array(dists)
                if len(dists):
                    min_indx = dists.argmin()
                    if dists.min() < 80:
                        tracks[min_indx].append([t, ankle])
                    else:
                        tracks.append([[t, ankle]])
                else:
                    tracks = [[[t, ankle]]]

            # drawing
            for idx, track in enumerate(tracks):
                for (t, ankle) in track:
                    cv2.circle(frame, tuple(ankle), 2, colors[idx % 8], 2, -1)

        # visualization
        cv2.imshow(f"frame_{cam_idx}", cv2.resize(frame, (960, 540)))

        if cv2.waitKey(1) == ord('c'):
            print(len(tracks[3]))

        if cv2.waitKey(1) == ord('q'):
            break

    else:
        break


with open("demo/ankle_tracks_123.json", "w") as f:
    json.dump(tracks[3], f)

vid.release()
cv2.destroyAllWindows()
