from .utils import get_confidence, body_face_assign, linear_assignment
from .detection import PersonDetector, FaceDetector
from modules.Aktar_OS.DataBase.cdm_db import cdmDB
# from service_lg.login_request import client
from .extraction import FeatureExtractor
from numpy.linalg import norm
from datetime import datetime
from queue import Queue
import numpy as np
# import requests
import cv2


class CDMEngine(object):
    def __init__(self, cfg=None):
        super(CDMEngine, self).__init__()
        # self.query_feat = None
        self.body_thresh = cfg['body_thresh']
        self.face_thresh = cfg['face_thresh']
        self.update_thres = cfg['update_threshold']
        self.update_ignore = cfg['update_ignore']
        self.iou_threshold_face_person = cfg['iou_threshold_face_person']
        self.save_with_face = cfg['save_with_face']
        self.competetive_body_ratio = cfg['competetive_body_ratio']
        self.competetive_body_area = cfg['competetive_body_area']
        self.competetive_face_ratio = cfg['competetive_face_ratio']
        self.competetive_face_area = cfg['competetive_face_area']
        # loading face and body detection modlues
        self.body_detector = PersonDetector(cfg['body_detection'])
        self.face_detector = FaceDetector(cfg['face_detection'])
        # loading face and body feature extractor modlue
        self.body_extractor = FeatureExtractor(cfg['body_extraction'])
        self.face_extractor = FeatureExtractor(cfg['face_extraction'])
        self.database = cdmDB(cfg["mongodb"])
        self.ids, body_att, face_att, self.time_stamps, self.id_counter = self.database.load_feature()
        self.bd_features, self.bd_count, self.bd_areas, self.bd_aspect_ratioes = body_att
        self.face_features, self.face_count, self.fa_areas, self.fa_aspect_ratioes = face_att

        if len(self.ids) > 0:
            self.q_idx_best_person = [1 for i in range(len(self.ids))]
            self.q_idx_best_face = [1 for i in range(len(self.ids))]
        else:
            self.q_idx_best_person = []
            self.q_idx_best_face = []

        # # Retrieve the CSRF token first
        # client.get("https://api.kachrobotics.com/api/user/set_csrf_cookie/")  # sets cookie
        # if 'csrftoken' in client.cookies:
        #     # Django 1.6 and up
        #     self.csrftoken = client.cookies['csrftoken']
        # else:
        #     # older versions
        #     self.csrftoken = client.cookies['csrf']

    def merge_id(self, face_query_id, face_num_queue, bd_query_id,  bd_num_queue):
        print(
            f"Person_{bd_query_id} will be merged  to person_{face_query_id} and will be deleted from database ")
        del self.bd_count[bd_num_queue]
        del self.bd_areas[bd_num_queue]
        del self.bd_aspect_ratioes[bd_num_queue]
        del self.time_stamps[bd_num_queue]
        del self.bd_features[bd_query_id]
        del self.q_idx_best_person[bd_num_queue]
        del self.ids[bd_num_queue]
        del self.q_idx_best_face[bd_num_queue]
        del self.face_features[bd_query_id]
        del self.fa_areas[bd_num_queue]
        del self.fa_aspect_ratioes[bd_num_queue]
        del self.face_count[bd_num_queue]
        self.database.delete_item(id=bd_query_id)

    def query_feature(self, norm_feat, features, thre_conf):
        found_conf = None
        query_id = 'unknown'
        max_conf = 0
        arg_max = None
        num_queue = None
        if len(features) > 0:
            conf = []
            for queue_features_key in features:
                qu_conf = get_confidence(
                    features[queue_features_key], norm_feat.T)
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
            if i in matched_indices[:, 1]:
                arg = np.where(matched_indices[:, 1] == i)[0][0]
                mapped[i] = faces[arg]
            else:
                mapped[i] = np.zeros(1)
        return mapped

    def step(self, img):
        if len(img.shape) != 3:
            print('Unknown Image Type !!!')
            return False

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        bodies, body_boxes = self.body_detector.detect_one(img, img_hsv)
        faces, face_boxes = self.face_detector.detect_one(img, img_hsv)

        matched_indices = np.empty(shape=(0, 2))
        if face_boxes != None and body_boxes != None:
            iou_matrix = body_face_assign(body_boxes, face_boxes)
            if min(iou_matrix.shape) > 0:
                a = (iou_matrix > self.iou_threshold_face_person).astype(np.int32)
                if a.sum(1).max() == 1 and a.sum(0).max() == 1:
                    matched_indices = np.stack(np.where(a), axis=1)
                elif a.sum(1).max() > 1 or a.sum(0).max() > 1:
                    matched_indices = linear_assignment(-iou_matrix)
                else:
                    matched_indices = np.empty(shape=(0, 2))

        if bodies != None:
            person_face = self.map_face_person(len(bodies), faces, matched_indices)
            for bd_idx, body in enumerate(bodies):
                bd_feat = self.body_extractor.extract_one(body)
                norm_bd_feat = bd_feat / norm(bd_feat, axis=1)
                bd_found_conf, bd_query_id, bd_num_queue = self.query_feature(norm_bd_feat, self.bd_features, self.body_thresh)
                x1, y1, x2, y2 = body_boxes[bd_idx]
                # intensity = np.mean(img_hsv[y1 : y2, x1 : x2, 2])
                bd_area = body.shape[1] * body.shape[0]
                bd_aspect_ratio = body.shape[0] / body.shape[1]
                best_body_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                face = person_face[bd_idx]
                if face.shape[0] > 1:
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
                    new_feat = np.expand_dims(norm_bd_feat, 0)
                    ba = Queue(maxsize=self.database.queue_size)
                    ba.put(norm_bd_feat)
                    self.bd_features[self.id_counter] = ba
                    self.ids.append(self.id_counter)
                    self.bd_count.append(1)
                    self.bd_areas.append(bd_area)
                    self.bd_aspect_ratioes.append(bd_aspect_ratio)
                    self.q_idx_best_person.append(1)
                    best_body_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.time_stamps.append([best_body_time_stamp])
                    self.database.update_body_feature(body, 1, norm_bd_feat, bd_area, bd_aspect_ratio,
                                                      id=self.id_counter, time_stamp=[best_body_time_stamp], method="save")
                    # self.faces.append(face)
                    fe = Queue(maxsize=self.database.queue_size)
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
                    self.database.update_face(face, face_count, norm_face_feat, fa_area, fa_aspect_ratio, id=self.id_counter)
                    self.id_counter += 1
                    print(best_body_time_stamp)
                else:
                    if face_query_id != bd_query_id and face_query_id != 'unknown':
                        print("Matching by face recognition")
                        force_update = True
                        query_id = face_query_id
                        num_queue = face_num_queue
                        if bd_query_id != 'unknown':
                            # url = 'https://api.kachrobotics.com/api/user/customer_data/'
                            # res = requests.put(url=url, json={"csrfmiddlewaretoken":self.csrftoken, "deleteId": bd_query_id, "mergeId": face_query_id})
                            # print("merge sync with negar: ", res.status_code)
                            self.merge_id(
                                face_query_id, face_num_queue, bd_query_id, bd_num_queue)
                            num_queue = num_queue - 1 if num_queue > bd_num_queue else num_queue
                    else:
                        print("Matching by person reid")
                        query_id = bd_query_id
                        num_queue = bd_num_queue
                        force_update = self.q_idx_best_face[num_queue] == 0 and face.shape[0] > 1 if self.save_with_face else False
                    print(f"Find a detected person_{query_id} confidence: {bd_found_conf}, {best_body_time_stamp}")

                    # if face is found and pass Conditions, will be update face in database
                    if face.shape[0] > 1:
                        upadte_by_area = fa_area > self.fa_areas[num_queue] if self.competetive_face_area else True
                        upadte_by_ratio = fa_aspect_ratio < self.fa_aspect_ratioes[
                            num_queue] if self.competetive_face_ratio else True
                        if upadte_by_area and upadte_by_ratio:
                            self.face_count[num_queue] += 1
                            self.fa_areas[num_queue] = fa_area
                            self.fa_aspect_ratioes[num_queue] = fa_aspect_ratio
                            # self.faces[num_queue] = face
                            self.database.update_face(
                                face, self.face_count[num_queue], norm_face_feat, fa_area, fa_aspect_ratio, id=query_id)
                        if face_found_conf < self.update_ignore:
                            # delete feature from front of queue by FIFO policy
                            if self.face_features[query_id].qsize() == self.database.queue_size:
                                temp_feature = self.face_features[query_id].get(
                                )
                            # recovery best appereance in queue if it has deleted from queue
                            if self.q_idx_best_face[num_queue] == self.database.queue_size:
                                self.face_features[query_id].get()
                                self.face_features[query_id].put(temp_feature)
                                self.q_idx_best_face[num_queue] = 1
                            self.face_features[query_id].put(norm_face_feat)
                            self.q_idx_best_face[num_queue] += 1
                        print("found face")
                    if bd_found_conf > self.update_thres or force_update:
                        # add feature in queue if body's confidence is between second threshold and 0.95
                        if bd_found_conf < self.update_ignore:
                            # delete feature from front of queue by FIFO policy
                            if self.bd_features[query_id].qsize() == self.database.queue_size:
                                temp_feature = self.bd_features[query_id].get()
                            # recovery best appereance in queue if it has deleted from queue
                            if self.q_idx_best_person[num_queue] == self.database.queue_size:
                                self.bd_features[query_id].get()
                                self.bd_features[query_id].put(temp_feature)
                                self.q_idx_best_person[num_queue] = 1
                            self.bd_features[query_id].put(norm_bd_feat)
                            self.q_idx_best_person[num_queue] += 1
                        body_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.time_stamps[num_queue].append(body_time_stamp)
                        # Update database  if best appereance is found
                        upadte_by_area = bd_area > self.bd_areas[num_queue] if self.competetive_body_area else True
                        upadte_by_ratio = bd_aspect_ratio > self.bd_aspect_ratioes[
                            num_queue] if self.competetive_body_ratio else True
                        # upadte_by_intensity = intensity >= self.intensity_thresh  if  self.competetive_body_intensity else True
                        upadte_by_face = fa_area > 0 if self.save_with_face else True
                        # if (upadte_by_area and upadte_by_ratio and upadte_by_intensity and upadte_by_face) or force_update:
                        if (upadte_by_area and upadte_by_ratio and upadte_by_face) or force_update:
                            print(f"Update person[{query_id}], ")
                            self.bd_areas[num_queue] = bd_area
                            self.bd_aspect_ratioes[num_queue] = bd_aspect_ratio
                            self.bd_count[num_queue] += 1
                            # self.bd_best_apper[self.id_counter][self.bd_best_count[self.id_counter]] = body
                            self.database.update_body_feature(body, self.bd_count[num_queue], norm_bd_feat, bd_area, bd_aspect_ratio,
                                                              id=query_id, time_stamp=self.time_stamps[num_queue])
                            self.q_idx_best_person[num_queue] = 1
                        else:
                            self.database.update_time(
                                id=query_id, time_stamp=self.time_stamps[num_queue])
