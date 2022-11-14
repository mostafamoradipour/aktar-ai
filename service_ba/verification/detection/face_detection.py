import numpy as np
import onnxruntime
import copy
import cv2

from .utils.general import check_img_size, non_max_suppression_face, scale_coords, xyxy2xywh
from .utils.utils import get_box, get_largest_face_img, letterbox, scale_coords_landmarks, get_faces, ignore_boxes


class FaceDetector(object):
    def __init__(self, cfg=None):
        super(FaceDetector, self).__init__()

        # TODO: 1. to add onnx runtime.
        #       2. to add openvino runtime for more efficiency on intel devices.

        self.img_size = cfg['img_size']
        self.conf_thres = cfg['conf_thres']
        self.iou_thres = cfg['iou_thres']

        self.min_area = cfg['min_area']
        self.min_ratio = cfg['min_ratio']
        self.max_ratio = cfg['max_ratio']
        self.ltrb = [cfg['left_pad'], cfg['top_pad'],
                     cfg['right_pad'], cfg['bottom_pad']]

        # device = 'cpu' if not torch.cuda.is_available() or cfg['device'] == 'cpu' else 'cuda:0'
        # self.device = torch.device(device)
        # self.model = attempt_load(cfg['weights'], map_location=self.device)

        _provider = ['CPUExecutionProvider'] if cfg['device'] == 'cpu' else ['CUDAExecutionProvider']
        self.session = onnxruntime.InferenceSession(cfg['weights'], providers=_provider)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def detect_one(self, orgimg):
        assert orgimg is not None, "Image is None"
        assert orgimg.shape[2] == 3, "Unknown Image Type"

        img0 = copy.deepcopy(orgimg)
        h0, w0 = orgimg.shape[:2]  # orig hw
        r = self.img_size / max(h0, w0)  # resize image to img_size
        if r != 1:  # always resize down, only resize up if training with augmentation
            interp = cv2.INTER_AREA if r < 1 else cv2.INTER_LINEAR
            img0 = cv2.resize(img0, (int(w0 * r), int(h0 * r)),
                              interpolation=interp)

        imgsz = check_img_size(
            self.img_size, s=32)  # check img_size

        img0 = letterbox(img0, new_shape=imgsz)[0]
        img = np.zeros((self.img_size, self.img_size, 3), dtype='uint8')
        pad0 = (self.img_size - img0.shape[0]) // 2
        pad1 = (self.img_size - img0.shape[1]) // 2
        img[pad0:self.img_size-pad0, pad1:self.img_size-pad1, :] = img0

        # Convert to 3xwxh
        img = img.transpose(2, 0, 1).copy()

        # Run inference
        # img = torch.from_numpy(img).to(self.device)
        # img = img.float()  # uint8 to fp16/32
        img = img.astype('float32')
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        # if img.ndimension() == 3:
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)

        # Inference
        # pred = self.model(img)[0]
        pred = self.session.run([self.output_name], {self.input_name: img})[0]
        # pred = torch.tensor(pred)

        # Apply NMS
        pred = non_max_suppression_face(pred, self.conf_thres, self.iou_thres)
        pred = ignore_boxes(boxes = pred, img_shape = img.shape[2:], 
                            ltrb = self.ltrb, min_area = self.min_area,
                            min_ratio = self.min_ratio, max_ratio = self.max_ratio) 
                            

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            gn = np.array(orgimg.shape)[[1, 0, 1, 0]] # normalization gain whwh
            # gn_lks = np.array(orgimg.shape)[[1, 0, 1, 0, 1, 0, 1, 0, 1, 0]] # normalization gain landmarks
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], orgimg.shape).round()

                # det[:, 5:15] = scale_coords_landmarks(
                #     img.shape[2:], det[:, 5:15], orgimg.shape).round()

                boxes = []
                for j in range(det.shape[0]):
                    xywh = (xyxy2xywh(det[j, :4].reshape(1, 4)) / gn).reshape(-1).tolist()
                    # conf = det[j, 4].cpu().numpy()
                    # landmarks = (det[j, 5:15].reshape(1, 10) / gn_lks).reshape(-1).tolist()
                    # class_num = det[j, 15].cpu().numpy()
                    box = get_box(orgimg, xywh)
                    boxes.append(box)

                # face = get_largest_face_img(orgimg, boxes)
                face = get_faces(orgimg, boxes)
                
                return face, boxes

            return None, None
