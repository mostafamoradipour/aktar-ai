from service_ba.verification import PersonVerifier
from service_cs.streaming import StreamerV1
from threading import Thread


class searchEngine():
    def __init__(self, cfg):
        self.verifier = PersonVerifier(cfg)
        self.vid_add = None
        self.running = False
        self.frame = 0

    def search(self):
        vid = StreamerV1(self.vid_add)
        while self.running:
            ret, frame = vid.read_last()
            if ret:
                self.verifier.verify(frame)
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
