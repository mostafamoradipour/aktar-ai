from service_fa.verification import FaceVerifier
from service_cs.streaming import StreamerV1


class searchEngine():
    def __init__(self, cfg):
        self.verifier = FaceVerifier(cfg)
        self.vid_add = cfg["test"]["video"]

    def search(self):
        vid = StreamerV1(self.vid_add)
        while True:
            ret, frame = vid.read_last()
            if ret:
                self.verifier.verify(frame)


if __name__ == "__main__":
    search = searchEngine()
    search.search()
