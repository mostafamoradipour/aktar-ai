from service_ba.verification import PersonVerifier
from service_cs.streaming import StreamerV1


class searchEngine():
    def __init__(self, cfg):
        self.verifier = PersonVerifier(cfg)
        self.vid_url = cfg["test"]["url"]

    def search(self):
        vid = StreamerV1(self.vid_url)
        while True:
            ret, frame = vid.read_last()
            if ret:
                self.verifier.verify(frame)


if __name__ == "__main__":
    search = searchEngine()
    search.search()
