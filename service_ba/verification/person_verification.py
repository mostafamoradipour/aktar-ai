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
        # self.features = self.database.load_feature()
        self.ids, self.areas, self.features, self.id_counter =self.database.load_feature()
        self.counter = 0

    def query_feature(self, norm_feat):
        find_face = False
        query_id = 'unknown'
        max_conf = 0
        if len(self.features) > 0 :
            conf = (1 + (self.features @ norm_feat.T)).reshape(-1)
            max_conf = conf.max() / 2
            arg_max = np.argmax(conf)
        if max_conf >= self.thresh:
            find_face = True
            query_id = self.ids[arg_max]
        
        return find_face, query_id


    
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
                find_person, query_id = self.query_feature(norm_feat)

                area = body.shape[1] * body.shape[0]

                if not find_person:
                    new_feat  = np.expand_dims(norm_feat, 0)

                    if self.features.shape[0] == 0:
                        self.features = new_feat
                    else:
                        self.features =  np.vstack((self.features, new_feat))
                    self.id_counter += 1
                    self.database.save_feature(body, norm_feat, area = area, id = self.id_counter)


                elif query_id != 'unknown':
                    if area >= self.areas[query_id]:
                        self.areas[query_id] = area
                        self.features[query_id] = norm_feat
                        self.database.update_feature(body, norm_feat, area = area, id = query_id)
                    
