from service_ba.verification import PersonVerifier
from service_cs.streaming import StreamerV1
from threading import Thread


class searchEngine():
    def __init__(self, cfg):
        self.verifier = PersonVerifier(cfg)
        self.cam_urls = []
        self.running = False

    def search(self):
        vids = []
        for cam_url in self.cam_urls:
            vids.append(StreamerV1(cam_url))
        while self.running:
            for vid in vids:
                ret, frame = vid.read_last()
                if ret:
                    self.verifier.verify(frame)
        for vid in vids:
            vid.release()

    def start(self):
        if self.running:
            return
        self.trd = Thread(target=self.search)
        self.running = True
        self.trd.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.trd.join()


if __name__ == "__main__":
    search = searchEngine()
    search.start()
    search.stop()
