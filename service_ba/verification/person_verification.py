from numpy.linalg import norm
import numpy as np
from .extraction import FeatureExtractor
from .detection import PersonDetector
from service_db.cdm_db import Database
from queue import Queue


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
        self.ids, self.areas, self.features, self.id_counter =self.database.load_feature()
        self.counter = 0
    
    def get_confidence(self, queue_features, norm_feat):
        '''
            geting max confidence for a peron's queue 
        '''
        queue_size = queue_features.qsize()
        features = [queue_features.queue[i] for i in range(queue_size)]
        features = np.array(features)
        confs = (1 + (features @ norm_feat)).reshape(-1)
        
        return confs.max() 



    def query_feature(self, norm_feat):
        find_face = False
        query_id = 'unknown'
        max_conf = 0
        arg_max = None
        if len(self.features) > 0:
            conf = []
            for queue_features_key  in self.features:
                person_conf = self.get_confidence(self.features[queue_features_key], norm_feat.T)
                conf.append(person_conf)

            # conf = (1 + (self.features @ norm_feat.T)).reshape(-1)
            conf = np.array(conf)
            max_conf = conf.max() / 2
            arg_max = np.argmax(conf)
        if max_conf >= self.thresh:
            find_face = True
            query_id = self.ids[arg_max]

        num_queue = arg_max
        
        return find_face, query_id, num_queue


    
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
                find_person, query_id, num_queue = self.query_feature(norm_feat)

                area = body.shape[1] * body.shape[0]

                if not find_person:
                    print(f"Find a new person[{query_id}]")
                    new_feat  = np.expand_dims(norm_feat, 0)
                    q = Queue(maxsize = self.database.queue_size)
                    q.put(norm_feat)
                    self.features[self.id_counter] = q
                    self.ids.append(self.id_counter)
                    self.areas.append(area)
                    self.database.save_feature(body, norm_feat, area = area, id = self.id_counter)
                    self.id_counter += 1


                elif query_id != 'unknown':
                    print(f"Find a detected person[{query_id}]")
                    if self.features[num_queue].qsize() == self.database.queue_size:
                        self.features[num_queue].get()

                    self.features[num_queue].put(norm_feat)

                    if area > self.areas[num_queue]:
                        print(f"Update person[{query_id}]")
                        self.areas[num_queue] = area
                        self.database.update_feature(body, norm_feat, area = area, id = query_id)
                    
