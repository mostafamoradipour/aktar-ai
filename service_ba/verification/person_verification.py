from numpy.linalg import norm
import numpy as np
from .extraction import FeatureExtractor
from .detection import PersonDetector
from service_db.cdm_db import Database


class PersonVerifier(object):
    def __init__(self, cfg=None):
        super(PersonVerifier, self).__init__()
        
        self.query_feat = None
        self.thresh = cfg['thresh']

        # loading face detection modlue
        self.detector = PersonDetector(cfg['detection'])

        # loading face feature extractor modlue
        self.extractor = FeatureExtractor(cfg['extraction'])
        self.database = Database(cfg["mongodb"])
        self.features = self.database.load_feature()
        self.counter = 0

    def query_feature(self, norm_feat):
        find_face = False
        max_conf = 0
        if len(self.features) > 0 :
            max_conf = (1 + (self.features @ norm_feat.T)).max() / 2
        if max_conf >= self.thresh:
            find_face = True
        
        return find_face


    
    def extract_feat(self, img):
        if len(img.shape) != 3:
            return None
        face = self.detector.detect_one(img)
        if face is not None:    
            feat = self.extractor.extract_one(face)
            norm_feat = feat / norm(feat, axis=1)
            return norm_feat
        else:
            return None

    def verify_one(self, img):
        if len(img.shape) != 3:
            # print('Unknown Image Type !!!')
            return False
        face = self.detector.detect_one(img)
        if face is not None:    
            feat = self.extractor.extract_one(face)
            norm_feat = feat / norm(feat, axis=1)
            conf = (1 + norm_feat @ self.query_feat.T).max() / 2
            if conf > self.thresh:
                return True
            else:
                return False
        else:
            return False


    def verify(self, img):
        if len(img.shape) != 3:
            # print('Unknown Image Type !!!')
            return False
        person = self.detector.detect_one(img)
        if person is not None:  
            for body in person:
                feat = self.extractor.extract_one(body)
                norm_feat = feat / norm(feat, axis=1)
                find_person = self.query_feature(norm_feat)

                if not find_person:
                    new_feat  = np.expand_dims(norm_feat, 0)

                    if self.features.shape[0] == 0:
                        self.features = new_feat
                    else:
                        self.features =  np.vstack((self.features, new_feat))
                    self.database.save_feature(body, norm_feat)
