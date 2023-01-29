from modules.Aktar_C.streaming import StreamerV1, resize
from threading import Thread
import numpy as np
import cv2


class streamEngine():
    def __init__(self):
        self.running = False
        self.opened = False

    def stream(self):
        cv2.namedWindow("Aktar-Stream", cv2.WINDOW_NORMAL)
        while self.running:
            frame = None
            if self.stream_urls[0]:
                ret0, frame0 = self.streamers[0].read_last()
                if ret0:
                    frame = frame0
            if self.stream_urls[1]:
                ret1, frame1 = self.streamers[1].read_last()
                if ret1:
                    frame = np.hstack((frame, frame1))
            if self.stream_urls[2]:
                ret2, frame2 = self.streamers[2].read_last()
                if ret2:
                    black_frame = np.zeros((frame2.shape), dtype="uint8")
                    frame1 = np.hstack((frame2, black_frame))
                if not self.stream_urls[3]:
                    frame = np.vstack((frame, frame1))
                else:
                    ret3, frame3 = self.streamers[3].read_last()
                    if ret3:
                        frame1 = np.hstack((frame2, frame3))
                        frame = np.vstack((frame, frame1))
            if ret0:
                # frame = resize(frame, width=1800)
                cv2.imshow("Aktar-Stream", frame)
                self.opened = True
            if cv2.waitKey(1) == ord('q'):
                self.running = False
            # if cv2.waitKey(1) and cv2.getWindowProperty("Aktar-C",cv2.WND_PROP_VISIBLE) < 1:
            #     break
        cv2.destroyAllWindows()
        self.opened = False
        for st in self.streamers:
            st.release()

    def start(self):
        if self.running:
            return
        self.streamers = []
        self.stream_urls = [None, None, None, None]
        for idx, url in enumerate(self.cam_urls[:4]):
            self.stream_urls[idx] = url
            streamer = StreamerV1(url)
            streamer.thread.start()
            self.streamers.append(streamer)
        del streamer
        self.running = True
        self.trd = Thread(target=self.stream)
        self.trd.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.trd.join()
