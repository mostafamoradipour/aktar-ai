import numpy as np
import yaml
import cv2


def f_distortion(x, y, mtx, dist):
    cx, cy, fx, fy = mtx[0, 2], mtx[1, 2], mtx[0, 0], mtx[1, 1]
    k1, k2, p1, p2, k3 = dist[0]
    xn = (x - cx) / fx
    yn = (y - cy) / fy
    r2 = xn ** 2 + yn ** 2
    coeff = (1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3)
    xd = xn * coeff * fx + cx
    yd = yn * coeff * fy + cy
    return (xd, yd)


def f_undistortion(xd, yd, mtx, dist):
    cx, cy, fx, fy = mtx[0, 2], mtx[1, 2], mtx[0, 0], mtx[1, 1]
    k1, k2, p1, p2, k3 = dist[0]
    xn = (xd - cx) / fx
    yn = (yd - cy) / fy
    r2 = xn ** 2 + yn ** 2
    coeff = (1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3)
    x = xn / coeff * fx + cx
    y = yn / coeff * fy + cy
    return (x, y)

def f_dist_undist(x, y, mtx, dist):
    xd, yd = f_distortion(x, y, mtx, dist)
    x, y = f_undistortion(xd, yd, mtx, dist)
    return (x, y)


class PointMapper(object):
    def __init__(self, cfg):
        self.mapping_data = {}
        self.num_of_cams = len(cfg.keys())
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
            self.mtx, self.dist = mtx, dist

    def map(self, cam_id, point):
        # to remove distortion
        xd, yd = point[0], point[1]
        xdu, ydu = f_undistortion(xd, yd, self.mtx, self.dist)
        x, y = xdu, ydu
        for _ in range(5):
            xdudu, ydudu = f_dist_undist(x, y, self.mtx, self.dist)
            x, y = xdu + x - xdudu, ydu + y - ydudu
        pixelPoint = (x, y)
        # to calculate the location
        physicalPoint = self.mapping_data[cam_id]['Q'] @ np.append(pixelPoint, 1).reshape(3, 1)
        x, z = (physicalPoint[:2] / physicalPoint[2]).reshape(-1).astype("int32")
        return (x, z)

    def height(self, cam_id, loc, point):
        # to remove distortion
        xd, yd = point[0], point[1]
        xdu, ydu = f_undistortion(xd, yd, self.mtx, self.dist)
        x, y = xdu, ydu
        for _ in range(5):
            xdudu, ydudu = f_dist_undist(x, y, self.mtx, self.dist)
            x, y = xdu + x - xdudu, ydu + y - ydudu
        point = (x, y)
        # to calculate the height
        P3 = np.array([[point[0], point[1], 1]]).T
        L = np.array([loc[0], loc[1], 1])
        b = -1 * self.mapping_data[cam_id]['P1'] @ L
        A = np.concatenate((self.mapping_data[cam_id]['P2'], P3), axis=1)
        x = np.linalg.inv(A.T @ A) @ (A.T @ b)
        height = x[0] * 1.8
        return height
