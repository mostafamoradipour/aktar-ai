from .verification import FaceVerifier
from .streaming import StreamerV1
from threading import Thread


class searchEngine():
    def __init__(self, cfg):
        self.verifier = FaceVerifier(cfg)
        self.vid_add = cfg["test"]["url"]

    def search(self):
        vid = StreamerV1(self.vid_add)
        while self.running:
            ret, frame = vid.read_last()
            if ret:
                self.verifier.verify(frame)

    def start(self):
        self.trd = Thread(target=self.search)
        self.running = True
        self.trd.start()

    def stop(self):
        self.running = False
        self.trd.join()


if __name__ == "__main__":
    search = searchEngine()
    search.search()
