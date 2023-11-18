import onnxruntime
import numpy as np
import glob
import cv2

from aktarai.tracking.utils import feature_cosine_distance as fcd


session = onnxruntime.InferenceSession("aktarai/recognition/weights/osnet_x0_25_msmt17.onnx", providers=['CUDAExecutionProvider'])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

img_pths = sorted(glob.glob('debug/*.png'))
print(img_pths)
features = []
for pth in img_pths:
    img = cv2.imread(pth)
    img = cv2.resize(img, (128, 256)) / 127.5 - 1
    input_data = np.expand_dims(img.transpose((2, 0, 1)), 0).astype('float32')
    features.append(session.run([output_name], {input_name: input_data})[0])

features = np.array(features).reshape(-1, 512)
dismat = fcd(features, features)
print(dismat, dismat.min(), dismat.max())
