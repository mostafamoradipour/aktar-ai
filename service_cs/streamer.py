from .streaming import StreamerV1, resize
from threading import Thread
import numpy as np
import cv2


class streamEngine():
    def __init__(self):
        self.cam_urls = None
        self.running = False

    def stream(self):
        streamers = []
        stream_urls = [None, None, None, None]
        for idx, url in enumerate(self.cam_urls[:4]):
            stream_urls[idx] = url
            streamers.append(StreamerV1(url))
        while self.running:
            frame = None
            if stream_urls[0]:
                ret0, frame0 = streamers[0].read_last()
                if ret0:
                    frame = frame0
            if stream_urls[1]:
                ret1, frame1 = streamers[1].read_last()
                if ret1:
                    frame = np.hstack((frame, frame1))
            if stream_urls[2]:
                ret2, frame2 = streamers[2].read_last()
                if ret2:
                    black_frame = np.zeros((frame2.shape), dtype="uint8")
                    frame1 = np.hstack((frame2, black_frame))
                if not stream_urls[3]:
                    frame = np.vstack((frame, frame1))
                else:
                    ret3, frame3 = streamers[3].read_last()
                    if ret3:
                        frame1 = np.hstack((frame2, frame3))
                        frame = np.vstack((frame, frame1))
            if ret0:
                frame = resize(frame, width=1800)
                cv2.imshow("Aktar-C", frame)
            if cv2.waitKey(1) == ord('q'):
                self.running = False
                break
            # if cv2.waitKey(1) and cv2.getWindowProperty("Aktar-C",cv2.WND_PROP_VISIBLE) < 1:
            #     break
        cv2.destroyAllWindows()
        for st in streamers:
            st.release()

    def start(self):
        if self.running:
            return
        self.trd = Thread(target=self.stream)
        self.running = True
        self.trd.start()
        self.trd.join()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.trd.join()

if __name__ == "__main__":
    stream = streamEngine()
    stream.start()
    stream.stop()


def Streamer(inputs):
    streamers = []
    stream_urls = [None, None, None, None]
    for idx, url in enumerate(inputs[:4]):
        stream_urls[idx] = url
        streamers.append(StreamerV1(url))
    while True:
        frame = None
        if stream_urls[0]:
            ret0, frame0 = streamers[0].read_last()
            if ret0:
                frame = frame0
        if stream_urls[1]:
            ret1, frame1 = streamers[1].read_last()
            if ret1:
                frame = np.hstack((frame, frame1))
        if stream_urls[2]:
            ret2, frame2 = streamers[2].read_last()
            if ret2:
                black_frame = np.zeros((frame2.shape), dtype="uint8")
                frame1 = np.hstack((frame2, black_frame))
            if not stream_urls[3]:
                frame = np.vstack((frame, frame1))
            else:
                ret3, frame3 = streamers[3].read_last()
                if ret3:
                    frame1 = np.hstack((frame2, frame3))
                    frame = np.vstack((frame, frame1))
        if ret0:
            frame = resize(frame, width=1800)
            cv2.imshow("Aktar-C", frame)
        if cv2.waitKey(1) == ord('q'):
            break
        # if cv2.waitKey(1) and cv2.getWindowProperty("Aktar-C",cv2.WND_PROP_VISIBLE) < 1:
        #     break
    cv2.destroyAllWindows()
    for st in streamers:
        st.release()
