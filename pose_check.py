import pickle
import cv2


with open('assets/all_frames_poses.pickle', 'rb') as handle:
    all_frames_poses = pickle.load(handle)

cam_numbers = len(all_frames_poses[0])

vid1 = cv2.VideoCapture("modules/Aktar_AI/DTwin/assets/parand/parand_123.avi")
vid2 = cv2.VideoCapture("modules/Aktar_AI/DTwin/assets/parand/parand_124.avi")
vid3 = cv2.VideoCapture("modules/Aktar_AI/DTwin/assets/parand/parand_125.avi")

frame_number = 0
while vid1.isOpened() and vid2.isOpened() and vid3.isOpened():
    ret1, frame1 = vid1.read()
    ret2, frame2 = vid2.read()
    ret3, frame3 = vid3.read()
    if ret1 and ret2 and ret3:
        frames = [frame1, frame2, frame3]
        all_cams_poses = all_frames_poses[frame_number]
        for cam_idx in range(cam_numbers):
            cam_poses = all_cams_poses[cam_idx]
            cam_frame = frames[cam_idx]
            for pose in cam_poses:
                conf = pose[-1]
                if conf < 15:
                    continue
                pose = pose[:-1].reshape(-1, 3)[:, :2]
                for joint in pose:
                    if (joint > 0).all():
                        cv2.circle(cam_frame, tuple(joint.astype("int")), 2, (0, 0, 255), 2, -1)
            cv2.imshow(f"frame_{cam_idx}", cv2.resize(cam_frame, (960, 540)))
        if cv2.waitKey(1) == ord('q'):
            break
    else:
        break
    frame_number += 1

vid1.release()
vid2.release()
vid3.release()
cv2.destroyAllWindows()
