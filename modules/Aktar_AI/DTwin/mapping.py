import numpy as np
import yaml
import cv2


class PointMapper(object):
    def __init__(self, cfg):
        self.mapping_data = {}
        for cam_id in cfg.keys():
            self.mapping_data[cam_id] = {}
            config = cfg[cam_id]
            with open(config['calibration_file']) as f:
                loadeddict = yaml.safe_load(f)
            mtx = loadeddict.get('camera_matrix')
            dist = loadeddict.get('dist_coeff')
            mtx = np.array(mtx)
            dist = np.array(dist)
            imagePoints = np.load(config['image_points']).astype('float32')
            physicalPoints = np.load(config['physical_points']).astype('float32')
            ret, rvec, tvec = cv2.solvePnP(physicalPoints, imagePoints, mtx, dist)
            assert ret, "error in calculating tvec and rvec"
            R, _ = cv2.Rodrigues(rvec)
            P = mtx @ np.hstack((R, tvec))
            P1 = np.concatenate((P[:, 0:1], P[:, 2:]), axis=1)
            self.mapping_data[cam_id]['P1'] = P1
            self.mapping_data[cam_id]['P2'] = P[:, 1:2]
            self.mapping_data[cam_id]['Q'] = np.linalg.inv(P1)


    def map(self, cam_id, loc_i):
        pixelPoint = np.array([loc_i[0], loc_i[1], 1])
        physicalPoint = self.mapping_data[cam_id]['Q'] @ pixelPoint
        x, z = physicalPoint[:2] / physicalPoint[2]
        return (x, z)

    def height(self, cam_id, foot_loc, head_point):
        P3 = np.array([[head_point[0], head_point[1], 1]]).T
        L = np.array([foot_loc[0], foot_loc[1], 1])
        b = -1 * self.mapping_data[cam_id]['P1'] @ L
        A = np.concatenate((self.mapping_data[cam_id]['P2'], P3), axis=1)
        x = np.linalg.inv(A.T @ A) @ (A.T @ b)
        height = x[0] * 1.35
        return height
