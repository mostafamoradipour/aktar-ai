# this is the main script of face feature extraction module.
# jobs:
#   1. gets the input face image.
#   2. rezie the image to the shape of 112 * 112
#   3. extract face feature of size 512.
#   4. returns the extracted feature.

import onnxruntime
import numpy as np
import cv2

from aktarai.detection.utils import extract_bodies


class BodyFeatureExtractor(object):
    def __init__(self, cfg=None):
        super(BodyFeatureExtractor, self).__init__()

        # TODO: to add openvino runtime for more efficiency on intel devices.

        _provider = ['CPUExecutionProvider'] if cfg['device'] == 'cpu' else ['CUDAExecutionProvider']
        self.session = onnxruntime.InferenceSession(cfg['weights'], providers=_provider)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_size = tuple(cfg['input_size'])

    def __call__(self, images, detections):
        '''
        this is the main function of this class:
            1. gets input face
            2. resize to 112 * 112
            3. extract feature and return it.
        '''
        input_data = []
        result = []
        for idx, img in enumerate(images):
            boxes = detections[idx]["boxes"]
            bodies = extract_bodies(img, boxes)
            features = []
            for body in bodies:
                img = cv2.resize(body, self.input_size) / 127.5 - 1
                input_data = np.expand_dims(img.transpose((2, 0, 1)), 0).astype('float32')
                features.append(self.session.run([self.output_name], {self.input_name: input_data})[0])
            result.append(features)
        return result


class FeatureExtractor(object):
    def __init__(self, cfg=None):
        super(FeatureExtractor, self).__init__()

        # TODO: to add openvino runtime for more efficiency on intel devices.

        _provider = ['CPUExecutionProvider'] if cfg['device'] == 'cpu' else ['CUDAExecutionProvider']
        self.session = onnxruntime.InferenceSession(cfg['weights'], providers=_provider)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_size = tuple(cfg['input_size'])

    def extract_one(self, img):
        '''
        this is the main function of this class:
            1. gets input face
            2. resize to 112 * 112
            3. extract feature and return it.
        '''
        img = cv2.resize(img, self.input_size) / 127.5 - 1
        input_data = np.expand_dims(
            img.transpose((2, 0, 1)), 0).astype('float32')
        feat = self.session.run([self.output_name], {self.input_name: input_data})[0]
        return feat
