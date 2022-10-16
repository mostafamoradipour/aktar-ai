from cv2 import imshow, waitKey, destroyAllWindows
from streaming import StreamerV1 as Streamer
from numpy import hstack, vstack
from time import time, sleep


def show_stream():
    input_uri = "rtsp://192.168.1.101:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800"
    stream1 = Streamer(input_uri, width=800, height=500)
    stream2 = Streamer(input_uri, width=800, height=500)
    stream3 = Streamer(input_uri, width=800, height=500)
    stream4 = Streamer(input_uri, width=800, height=500)
    while True:
        ret, frame1 = stream1.read_last()
        ret, frame2 = stream2.read_last()
        ret, frame3 = stream3.read_last()
        ret, frame4 = stream4.read_last()
        if ret:
            frame1 = hstack((frame1, frame2))
            frame2 = hstack((frame3, frame4))
            frame = vstack((frame1, frame2))
            imshow("frame", frame)
        if waitKey(1) == ord('q'):
            break
    stream1.release()
    stream2.release()
    stream3.release()
    stream4.release()
    destroyAllWindows()


if __name__ == "__main__":
    show_stream()
