from ultralytics import YOLO
from copy import deepcopy
import numpy as np
import json
import cv2

# from modules.Aktar_AI.DetRec.extraction import FeatureExtractor


frame_skip = 2
frame_count = 0

COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255)]
# bfe_config = {'device': 'gpu', 'weights': 'modules/Aktar_AI/DetRec/extraction/weights/w600k_mbf.onnx', 'input_size': [112, 112]}
body_detector = YOLO('weights/yolov8s-pose.pt')
# body_feature_extractor = FeatureExtractor(bfe_config)

cap = cv2.VideoCapture('/mnt/storage/projects/Aktar/Mapping/data/parand-sub/video/cam4.avi')

data = []

while True:
    ret, frame = cap.read()
    if ret:
        record = []

        frame_count += 1
        if frame_count > 4500:
            break 
        # if frame_count % (frame_skip + 1) != 1:
        #     continue
        
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = body_detector(frame)[0]
        bconfs = result.boxes.conf
        try:
            keypoints = result.keypoints[bconfs > 0.75]
            boxes = result.boxes.xyxy[bconfs > 0.75]
            confs = keypoints.conf
            for idx, kps in enumerate(keypoints):
                kps = kps.xy.cpu().numpy().astype("int32").reshape(-1, 2)
                cnfs = confs[idx].cpu().numpy().reshape(-1)
                box = boxes[idx].cpu().numpy().astype("int32").reshape(-1)
                record.append({"box": box.tolist(), "kpts": kps.tolist(), "cnfs": cnfs.tolist()})
                for point in kps:
                    cv2.circle(frame, tuple(point), 5, COLORS[idx], -1)
                cv2.rectangle(frame, tuple(box[:2]), tuple(box[2:]), (0, 255, 0), 2)
            cv2.putText(frame, str(len(boxes)), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        except:
            pass
        
        data.append(deepcopy(record))

        cv2.imshow("result", frame)        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    else:
        break

cap.release()
cv2.destroyAllWindows()

with open("demo/parand-sub/cam4.json", "w") as f:
    json.dump(data, f)


'''
# Tracker
# Open the video file
# video_path = "/mnt/storage/projects/Aktar/Mapping/data/home-mostafa/video/cam_2_light_off.avi"
video_path = "/mnt/storage/projects/Aktar/Mapping/data/parand/video/out_2.mp4"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.5)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
'''
