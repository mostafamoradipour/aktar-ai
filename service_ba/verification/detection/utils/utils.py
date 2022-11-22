from numpy import argsort, mod, logical_and, mean, array
import cv2


def ignore_boxes(img_hsv, boxes, img_shape, ltrb = [30, 10, 20, 10], min_area = 1000, min_ratio = 1.4, max_ratio = 4, min_intensity = 40, ):
    ### Filter by margin
    w, h = img_shape
    x1_y1_min = (boxes[0][:, :2] < [ltrb[0], ltrb[1]])
    x2_y2_max = (boxes[0][:, 2:4] > ([h - ltrb[2], w - ltrb[2]]) )

    margin_indexes = x1_y1_min.sum(axis=1) + x2_y2_max.sum(axis=1)
    margin_indexes = margin_indexes < 1

    ### Filter by aspect ratio and area 
    good_area_indexes = (boxes[0][:,3] - boxes[0][:,1]) * (boxes[0][:,2] - boxes[0][:,0])> min_area
    
    aspect_ratio = (boxes[0][:,3] - boxes[0][:,1]) / (boxes[0][:,2] - boxes[0][:,0])
    good_ratio_indexes = logical_and((aspect_ratio <max_ratio), (aspect_ratio > min_ratio))

    # Filter by intensity
    intensity_boxes = array([mean(img_hsv[int(i[1]) : int(i[3]), int(i[0]) : int(i[2]), 2]) for i in boxes[0]])
    good_intensity_index = intensity_boxes > min_intensity  
  
    indexes = logical_and(good_ratio_indexes, good_area_indexes, margin_indexes)
    indexes = logical_and(indexes, good_intensity_index)

    
    return   [boxes[0][indexes]] #boxes[indexes]


def get_box(img, xywh):
    h,w,c = img.shape
    x1 = int(xywh[0] * w - 0.5 * xywh[2] * w)
    y1 = int(xywh[1] * h - 0.5 * xywh[3] * h)
    x2 = int(xywh[0] * w + 0.5 * xywh[2] * w)
    y2 = int(xywh[1] * h + 0.5 * xywh[3] * h)
    return (x1, y1, x2, y2)


def get_largest_face_img(img, boxes):
    areas = [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes]
    box = boxes[int(argsort(areas)[-1])]
    face = img[box[1]:box[3], box[0]:box[2], :]
    if face.shape[0] * face.shape[1] > 200:
        return face
    else:
        return None


def get_objects(img, boxes):
    faces = []
    for box in boxes:
        face = img[box[1]:box[3], box[0]:box[2], :]
        if face.shape[0] * face.shape[1] > 200:
            faces.append(face)
    return faces


def show_results(img, xywh, conf, landmarks, class_num):
    h, w, c = img.shape
    tl = 1 or round(0.002 * (h + w) / 2) + 1  # line/font thickness
    x1 = int(xywh[0] * w - 0.5 * xywh[2] * w)
    y1 = int(xywh[1] * h - 0.5 * xywh[3] * h)
    x2 = int(xywh[0] * w + 0.5 * xywh[2] * w)
    y2 = int(xywh[1] * h + 0.5 * xywh[3] * h)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0),
                    thickness=tl, lineType=cv2.LINE_AA)

    clors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (0, 255, 255)]

    for i in range(5):
        point_x = int(landmarks[2 * i] * w)
        point_y = int(landmarks[2 * i + 1] * h)
        cv2.circle(img, (point_x, point_y), tl+1, clors[i], -1)

    tf = max(tl - 1, 1)  # font thickness
    label = str(conf)[:5]
    cv2.putText(img, label, (x1, y1 - 2), 0, tl / 3,
                [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    return img


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    # only scale down, do not scale up (for better test mAP)
    if not scaleup:
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
        new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = mod(dw, 64), mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / \
            shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def scale_coords_landmarks(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0],
                    img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / \
            2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2, 4, 6, 8]] -= pad[0]  # x padding
    coords[:, [1, 3, 5, 7, 9]] -= pad[1]  # y padding
    coords[:, :10] /= gain
    #clip_coords(coords, img0_shape)
    coords[:, 0].clip(0, img0_shape[1])  # x1
    coords[:, 1].clip(0, img0_shape[0])  # y1
    coords[:, 2].clip(0, img0_shape[1])  # x2
    coords[:, 3].clip(0, img0_shape[0])  # y2
    coords[:, 4].clip(0, img0_shape[1])  # x3
    coords[:, 5].clip(0, img0_shape[0])  # y3
    coords[:, 6].clip(0, img0_shape[1])  # x4
    coords[:, 7].clip(0, img0_shape[0])  # y4
    coords[:, 8].clip(0, img0_shape[1])  # x5
    coords[:, 9].clip(0, img0_shape[0])  # y5
    return coords


def get_faces(img, boxes):
    faces = []
    for box in boxes:
        face = img[box[1]:box[3], box[0]:box[2], :]
        if face.shape[0] * face.shape[1] > 200:
            faces.append(face)
    return faces