import numpy as np


class StaticKF(object):
    def __init__(self, init_height=None):
        if init_height:
            self.x = init_height
        else:
            self.x = 180.
        self.iter = 1 

    def update(self, ms_height):
        if ms_height:
            kalman_gain = 1 / self.iter
            inovation = ms_height - self.x
            self.x = self.x + kalman_gain * inovation
            self.iter += 1


class DynamicKF(object):
    def __init__(self,
                 init_location=None,
                 dt=0.4,
                 u_x=1.,
                 u_y=1.,
                 std_acc=1.,
                 x_std_meas=1.,
                 y_std_meas=1.):
        """
        :param dt: sampling time (time for 1 cycle)
        :param u_x: acceleration in x-direction
        :param u_y: acceleration in y-direction
        :param std_acc: process noise magnitude
        :param x_std_meas: standard deviation of the measurement in x-direction
        :param y_std_meas: standard deviation of the measurement in y-direction
        """
        # Define sampling time
        self.dt = dt
        # Define the  control input variables
        self.u = np.matrix([[u_x], [u_y]], dtype="float32")
        # Intial State
        self.x = np.matrix([[0.], [0.], [0.], [0.]], dtype="float32")
        self.x[:2] = np.array(init_location, dtype="float32").reshape(2, 1)
        # Define the State Transition Matrix A
        self.A = np.matrix([[1., 0., self.dt, 0.],
                            [0., 1., 0., self.dt],
                            [0., 0., 1., 0.],
                            [0., 0., 0., 1.]], dtype="float32")
        # Define the Control Input Matrix B
        self.B = np.matrix([[(self.dt**2)/2, 0.],
                            [0., (self.dt**2)/2],
                            [self.dt, 0.],
                            [0., self.dt]], dtype="float32")
        # Define Measurement Mapping Matrix
        self.H = np.matrix([[1., 0., 0., 0.],
                            [0., 1., 0., 0.]], dtype="float32")
        # Initial Process Noise Covariance
        self.Q = np.matrix([[(self.dt**4)/4, 0., (self.dt**3)/2, 0.],
                            [0., (self.dt**4)/4, 0., (self.dt**3)/2],
                            [(self.dt**3)/2, 0., self.dt**2, 0.],
                            [0., (self.dt**3)/2, 0., self.dt**2]], dtype="float32") * std_acc**2
        # Initial Measurement Noise Covariance
        self.R = np.matrix([[x_std_meas**2, 0.],
                           [0., y_std_meas**2]])
        # Initial Covariance Matrix
        self.P = np.eye(self.A.shape[1], dtype="float32")

    def _predict(self):
        # Update time state
        # x_k =Ax_(k-1) + Bu_(k-1)     Eq.(9)
        self.x = np.dot(self.A, self.x) + np.dot(self.B, self.u)
        # Calculate error covariance
        # P= A*P*A' + Q               Eq.(10)
        self.P = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q
        return self.x[0:2]

    def _update(self, z):
        # S = H*P*H'+R
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        # Calculate the Kalman Gain
        # K = P * H'* inv(H*P*H'+R)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))  # Eq.(11)
        self.x = np.round(
            self.x + np.dot(K, (z - np.dot(self.H, self.x))))  # Eq.(12)
        I = np.eye(self.H.shape[1])
        # Update error covariance matrix
        self.P = (I - (K * self.H)) * self.P  # Eq.(13)
        return self.x[0:2]

    def update(self, ms_location):
        if ms_location:
            z = np.array(ms_location).reshape((2, 1))
            self._predict()
            self._update(z)
