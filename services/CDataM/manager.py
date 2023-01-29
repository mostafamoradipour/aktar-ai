from modules.Aktar_AI.DetRec.verification import PersonVerifier
from modules.Aktar_C.streaming import StreamerV1
from threading import Thread


class CDManager():
    def __init__(self, cfg):
        self.verifier = PersonVerifier(cfg)
        self.cam_urls = None
        self.running = False

    def run(self):
        vids = []
        for cam_url in self.cam_urls:
            streamer = StreamerV1(cam_url)
            streamer.thread.start()
            vids.append(streamer)
            del streamer
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
        self.trd = Thread(target=self.run)
        self.running = True
        self.trd.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.trd.join()


if __name__ == "__main__":
    search = CDManager()
    search.start()
    search.stop()
