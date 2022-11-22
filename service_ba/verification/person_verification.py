from .detection import PersonDetector, FaceDetector
from .extraction import FeatureExtractor
from service_db.cdm_db import Database
from time import gmtime, strftime
from numpy.linalg import norm
from queue import Queue
import numpy as np
import cv2


def linear_assignment(cost_matrix):
  try:
    import lap
    _, x, y = lap.lapjv(cost_matrix, extend_cost=True)
    return np.array([[y[i],i] for i in x if i >= 0]) #
  except ImportError:
    from scipy.optimize import linear_sum_assignment
    x, y = linear_sum_assignment(cost_matrix)
    return np.array(list(zip(x, y)))


def linear_assignment(cost_matrix):
  try:
    import lap
    _, x, y = lap.lapjv(cost_matrix, extend_cost=True)
    return np.array([[y[i],i] for i in x if i >= 0]) #
  except ImportError:
    from scipy.optimize import linear_sum_assignment
    x, y = linear_sum_assignment(cost_matrix)
    return np.array(list(zip(x, y)))


class PersonVerifier(object):
    def __init__(self, cfg=None):
        super(PersonVerifier, self).__init__()
        self.query_feat = None
        self.body_thresh = cfg['body_thresh']
        self.face_thresh = cfg['face_thresh']
        self.update_thres = cfg['update_threshold']
        self.update_ignore = cfg['update_ignore']
        self.iou_threshold_face_person = cfg['iou_threshold_face_person']
        self.intensity_thresh = cfg['intensity_thresh']
        self.save_with_face = cfg['save_with_face']
        self.competetive_body_ratio = cfg['competetive_body_ratio']
        self.competetive_body_area = cfg['competetive_body_area']
        self.competetive_body_intensity = cfg['competetive_body_intensity']
        self.competetive_face_ratio = cfg['competetive_face_ratio']
        self.competetive_face_area = cfg['competetive_face_area']


        # loading face and body detection modlues
        self.body_detector = PersonDetector(cfg['body_detection'])
        self.face_detector = FaceDetector(cfg['face_detection'])

        # loading face and body feature extractor modlue
        self.body_extractor = FeatureExtractor(cfg['body_extraction'])
        self.face_extractor = FeatureExtractor(cfg['face_extraction'])

        self.database = Database(cfg["mongodb"])
        # self.ids, self.bd_best_count, self.face_count, self.bd_areas, self.bd_aspect_ratioes, self.features, self.faces, self.time_stamps, self.id_counter =
        self.ids, body_att, face_att, self.time_stamps, self.id_counter = self.database.load_feature()
        self.bd_features, self.bd_count, self.bd_areas, self.bd_aspect_ratioes = body_att
        self.face_features, self.face_count, self.fa_areas, self.fa_aspect_ratioes = face_att

        if len(self.ids)>0:
            self.q_idx_best_person = [1 for i in range(len(self.ids))]
            self.q_idx_best_face = [1 for i in range(len(self.ids))]
        else:
            self.q_idx_best_person = []
            self.q_idx_best_face = []

    
    def get_confidence(self, queue_features, norm_feat):
        '''
            geting max confidence for a peron's queue 
        '''
        queue_size = queue_features.qsize()
        if queue_size > 0:
            features = [queue_features.queue[i] for i in range(queue_size)]
            features = np.array(features)
            confs = (1 + (features @ norm_feat)).reshape(-1)
        else:
            return 0
        
        return confs.max() 

    def assign_face_person(self, person_boxes, face_boxes):
        """
        From SORT: Computes IOU between two bboxes in the form [x1,y1,x2,y2]
        """
        person_boxes = np.expand_dims(person_boxes, 0)
        face_boxes = np.expand_dims(face_boxes, 1)        
        xx1 = np.maximum(face_boxes[..., 0], person_boxes[..., 0])
        yy1 = np.maximum(face_boxes[..., 1], person_boxes[..., 1])
        xx2 = np.minimum(face_boxes[..., 2], person_boxes[..., 2])
        yy2 = np.minimum(face_boxes[..., 3], person_boxes[..., 3])
        w = np.maximum(0., xx2 - xx1)
        h = np.maximum(0., yy2 - yy1)
        wh = w * h
        o = wh / ((face_boxes[..., 2] - face_boxes[..., 0]) * (face_boxes[..., 3] - face_boxes[..., 1])                                      
            + (person_boxes[..., 2] - person_boxes[..., 0]) * (person_boxes[..., 3] - person_boxes[..., 1]) - wh)                                              
        return(o) 
        


    def query_feature(self, norm_feat, features, thre_conf):
        found_conf = False
        query_id = 'unknown'
        max_conf = 0
        arg_max = None
        num_queue = None
        if len(features) > 0:
            conf = []
            for queue_features_key  in features:
                qu_conf = self.get_confidence(features[queue_features_key], norm_feat.T)
                conf.append(qu_conf)

            # conf = (1 + (self.features @ norm_feat.T)).reshape(-1)
            conf = np.array(conf)
            max_conf = conf.max() / 2
            arg_max = np.argmax(conf)
        if max_conf >= thre_conf:
            found_conf = max_conf
            query_id = self.ids[arg_max]
            num_queue = arg_max
        
        return found_conf, query_id, num_queue

    def map_face_person(self, num_person, faces, matched_indices):
        mapped = dict()

        for i in range(num_person):
            if  i in matched_indices[:,1]:
                arg = np.where(matched_indices[:,1]== i)[0][0]
                mapped[i] = faces[arg]
            else:
                 mapped[i] = np.zeros(1)
        return mapped



    def verify(self, img):
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        if len(img.shape) != 3:
            print('Unknown Image Type !!!')
            return False
        person, person_boxes = self.body_detector.detect_one(img)
        faces, face_boxes = self.face_detector.detect_one(img)

        matched_indices = np.empty(shape=(0,2))
        if face_boxes != None and person_boxes != None:
            iou_matrix = self.assign_face_person(person_boxes, face_boxes)
            if min(iou_matrix.shape) > 0:
                a = (iou_matrix > self.iou_threshold_face_person).astype(np.int32)
                if a.sum(1).max() == 1 and a.sum(0).max() == 1:
                    matched_indices = np.stack(np.where(a), axis=1)
                elif a.sum(1).max() > 1 or a.sum(0).max() > 1:
                    matched_indices = linear_assignment(-iou_matrix)
                else:
                    matched_indices = np.empty(shape=(0,2))

        if person is not None:  
            person_face = self.map_face_person(len(person), faces, matched_indices)
            
            for bd_idx, body in enumerate(person):
                bd_feat = self.body_extractor.extract_one(body)
                norm_bd_feat = bd_feat / norm(bd_feat, axis=1)
                bd_found_conf, bd_query_id, bd_num_queue = self.query_feature(norm_bd_feat, self.bd_features, self.body_thresh)
                x1,y1, x2,y2 = person_boxes[bd_idx] 
                intensity = np.mean(img_hsv[y1 : y2, x1 : x2, 2])
                bd_area = body.shape[1] * body.shape[0]
                bd_aspect_ratio = body.shape[0] / body.shape[1]
                best_body_time_stamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                face = person_face[bd_idx]
                if  face.shape[0] > 1:
                    face_feat = self.face_extractor.extract_one(face)
                    norm_face_feat = face_feat / norm(face_feat, axis=1)
                    face_found_conf, face_query_id, face_num_queue = self.query_feature(norm_face_feat, self.face_features, self.face_thresh)
                    fa_area = face.shape[1] * face.shape[0]
                    fa_aspect_ratio = face.shape[0] / face.shape[1]
                else:
                    face_found_conf = False
                    face_query_id = 'unknown'
                    fa_area = 0 
                    fa_aspect_ratio = 4

                if not bd_found_conf and not face_found_conf:
                    print(f"Find a new person_{self.id_counter}")
                    new_feat  = np.expand_dims(norm_bd_feat, 0)
                    ba = Queue(maxsize = self.database.queue_size)
                    ba.put(norm_bd_feat)
                    self.bd_features[self.id_counter] = ba
                    self.ids.append(self.id_counter)
                    self.bd_count.append(1)
                    self.bd_areas.append(bd_area)
                    self.bd_aspect_ratioes.append(bd_aspect_ratio)
                    self.q_idx_best_person.append(1)
                    best_body_time_stamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    self.time_stamps.append([best_body_time_stamp])
                    
                    self.database.update_body_feature(body, 1, norm_bd_feat, bd_area, bd_aspect_ratio, 
                                                        id = self.id_counter, time_stamp = [best_body_time_stamp], method = "save")
                    
                    # self.faces.append(face)
                    fe = Queue(maxsize = self.database.queue_size)
                    if fa_area == 0:
                        self.face_count.append(0)
                        face_count = 0
                        norm_face_feat = None
                        self.q_idx_best_face.append(0)
                    else:
                        fe.put(norm_face_feat)
                        self.q_idx_best_face.append(1)
                        self.face_count.append(1)
                        face_count = 1

                    self.face_features[self.id_counter] = fe
                    self.fa_areas.append(fa_area)
                    self.fa_aspect_ratioes.append(fa_aspect_ratio)

                    self.database.update_face(face, face_count, norm_face_feat, fa_area, fa_aspect_ratio, id = self.id_counter)

                    self.id_counter += 1
                    print(best_body_time_stamp)

                else:
                    if face_query_id != bd_query_id and face_query_id != 'unknown':
                        print("Matching by face recognition")
                        force_update = True
                        query_id = face_query_id
                        num_queue = face_num_queue
                        
                    else:
                        print("Matching by person reid")
                        query_id = bd_query_id
                        num_queue = bd_num_queue
                        force_update = self.q_idx_best_face[num_queue] == 0 and face.shape[0] > 1  if  self.save_with_face else  False

                    print(f"Find a detected person_{query_id} confidence: {bd_found_conf}, {best_body_time_stamp}")
                    # if face is found and pass Conditions, will be update face in database 
                    if  face.shape[0] > 1:
                        upadte_by_area = fa_area > self.fa_areas[num_queue] if self.competetive_face_area else True
                        upadte_by_ratio = fa_aspect_ratio < self.fa_aspect_ratioes[num_queue] if  self.competetive_face_ratio else True
                        if upadte_by_area and upadte_by_ratio:
                            self.face_count[num_queue] += 1
                            self.fa_areas[num_queue] = fa_area
                            self.fa_aspect_ratioes[num_queue] = fa_aspect_ratio
                            # self.faces[num_queue] = face
                            self.database.update_face(face, self.face_count[num_queue], norm_face_feat, fa_area,fa_aspect_ratio, id = query_id)


                        if face_found_conf < self.update_ignore:
                            ## delete feature from front of queue by FIFO policy
                            if self.face_features[num_queue].qsize() == self.database.queue_size:
                                temp_feature = self.face_features[num_queue].get()

                            ## recovery best appereance in queue if it has deleted from queue 
                            if self.q_idx_best_face[num_queue] == self.database.queue_size:
                                self.face_features[num_queue].get()
                                self.face_features[num_queue].put(temp_feature)
                                self.q_idx_best_face[num_queue] = 1

                            self.face_features[num_queue].put(norm_face_feat)
                            self.q_idx_best_face[num_queue] += 1
                        print("found face")
                        
                    

                    if bd_found_conf > self.update_thres or force_update:                        
                        ## add feature in queue if body's confidence is between second threshold and 0.95 
                        if bd_found_conf < self.update_ignore:
                            ## delete feature from front of queue by FIFO policy
                            if self.bd_features[num_queue].qsize() == self.database.queue_size:
                                temp_feature = self.bd_features[num_queue].get()

                            ## recovery best appereance in queue if it has deleted from queue 
                            if self.q_idx_best_person[num_queue] == self.database.queue_size:
                                self.bd_features[num_queue].get()
                                self.bd_features[num_queue].put(temp_feature)
                                self.q_idx_best_person[num_queue] = 1

                            self.bd_features[num_queue].put(norm_bd_feat)
                            self.q_idx_best_person[num_queue] += 1

                        body_time_stamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        self.time_stamps[num_queue].append(body_time_stamp)
                        
                        ## Update database  if best appereance is found
                        upadte_by_area = bd_area > self.bd_areas[num_queue] if self.competetive_body_area else True
                        upadte_by_ratio = bd_aspect_ratio > self.bd_aspect_ratioes[num_queue] if  self.competetive_body_ratio else True
                        upadte_by_intensity = intensity >= self.intensity_thresh  if  self.competetive_body_intensity else True
                        upadte_by_face = fa_area > 0  if  self.save_with_face else True

                        if force_update or upadte_by_face:
                            print("fd")

                        if (upadte_by_area and upadte_by_ratio and upadte_by_intensity and upadte_by_face) or force_update:
                            print(f"Update person[{query_id}], ")
                            self.bd_areas[num_queue] = bd_area
                            self.bd_aspect_ratioes[num_queue] = bd_aspect_ratio
                            self.bd_count[num_queue] += 1
                            # self.bd_best_apper[self.id_counter][self.bd_best_count[self.id_counter]] = body
                            
                            self.database.update_body_feature(body, self.bd_count[num_queue], norm_bd_feat, bd_area, bd_aspect_ratio, 
                                                        id = query_id, time_stamp = self.time_stamps[num_queue])

                            self.q_idx_best_person[num_queue] = 1
                        

                        else:
                            self.database.update_time(id=query_id, time_stamp=self.time_stamps[num_queue])
