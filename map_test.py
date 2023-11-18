import yaml
import cv2

from aktarai.mapping import PointMapper


def main(user="mostafa"):
    with open("config-test.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]
    cam_id = 2
    mapper = PointMapper(cfg["engine"]["mapping"])
    # mapper.refine(cam_id)
    vid = cv2.VideoCapture(cfg["video"][cam_id])
    ret, frame = vid.read()
    assert ret, "video link can't be read"
    imagePoints, physicalPoints = mapper.mapping_data[cam_id]["measurements"][2:]
    print(physicalPoints)
    for number, pp in enumerate(physicalPoints):
        keypoint = tuple(imagePoints[number].astype("int"))
        center = mapper.map(cam_id, pp)
        cv2.putText(frame, str(number+1), keypoint, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.circle(frame, keypoint, 5, (0, 255 , 0), -1)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
    
    # result = mapper.imap2(cam_id, center, Y=0)
    # print(result)
    
    cv2.imshow("image", frame)
    cv2.waitKey(0)


if __name__=="__main__":
    main(user="parand-sub")
