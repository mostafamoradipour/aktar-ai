from cv2 import VideoCapture, CAP_GSTREAMER, INTER_AREA
from threading import Thread, Condition, Event
from subprocess import check_output
from cv2 import resize as cv_resize
from urllib.parse import urlparse
from numpy import ndarray, uint8
from collections import deque
from time import sleep
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GstApp


def resize(image, width=None, height=None, inter=INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # check to see if the height is None
    elif height is None:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))
    else:
        dim = (width, height)
    # resize the image
    resized = cv_resize(image, dim, interpolation=inter)
    # return the resized image
    return resized


class StreamerV1(object):
    def __init__(self, input_uri, width=None, height=None, max_queue_size=1, frame_skip=0, preprocess=None, GStreamer=False):
        super(StreamerV1, self).__init__()

        self.input_uri = input_uri
        self.protocol = self._parse_uri(self.input_uri)
        self.width = width
        self.height = height

        if GStreamer:
            self.stream = VideoCapture(self.gst_cap_pipeline(), CAP_GSTREAMER)
        else:
            self.stream = VideoCapture(input_uri)

        assert isinstance(max_queue_size, int)
        self.max_queue_size = max_queue_size
        self.queue = deque([])

        self.frame_skip = frame_skip
        self.preprocess = preprocess
        self.exit_event = Event()
        self.cond = Condition()
        self.thread = Thread(target=self.read_input_uri, name='Streamer')

    def read_input_uri(self):
        counter = 0
        while not self.exit_event.is_set():
            ret, frame = self.stream.read()
            # sleep(0.083333333+0.5)
            counter += 1
            with self.cond:
                if not ret:
                    self.exit_event.set()
                    self.cond.notify()
                    break
                if counter % (self.frame_skip + 1) == 0:
                    counter = 0
                    if self.preprocess:
                        frame = self.preprocess(frame)
                        if frame:
                            self.queue.append(frame)
                    else:
                        self.queue.append(frame)
                    if self.max_queue_size > 0:
                        while len(self.queue) > self.max_queue_size:
                            self.queue.popleft()
                    self.cond.notify()

    def read_last(self):
        with self.cond:
            while len(self.queue) == 0 and not self.exit_event.is_set():
                self.cond.wait()
            if len(self.queue) == 0 and self.exit_event.is_set():
                return False, None
            frame = self.queue.pop()
            self.cond.notify()
        frame = resize(frame, width=self.width, height=self.height)
        return True, frame

    def read_first(self):
        with self.cond:
            while len(self.queue) == 0 and not self.exit_event.is_set():
                self.cond.wait()
            if len(self.queue) == 0 and self.exit_event.is_set():
                return False, None
            frame = self.queue.popleft()
            self.cond.notify()
        frame = resize(frame, width=self.width, height=self.height)
        return True, frame

    def release(self):
        with self.cond:
            self.exit_event.set()
            self.cond.notify()
        self.thread.join()
        self.queue.clear()
        self.stream.release()

    def gst_cap_pipeline(self):
        gst_elements = str(check_output('gst-inspect-1.0'))
        if 'nvvidconv' in gst_elements and self.protocol != 'v4l2':
            # format conversion for hardware decoder
            cvt_pipeline = (
                'nvvidconv interpolation-method=5 ! '
                'video/x-raw, format=BGRx ! '
                'videoconvert ! appsink sync=false'
            )
        else:
            cvt_pipeline = (
                'videoscale ! video/x-raw !'
                'videoconvert ! appsink sync=false'
            )
        if self.protocol == 'csi':
            pipeline = 'nvarguscamerasrc sensor_id=%s ! video/x-raw(memory:NVMM), format=NV12 ! ' % (
                self.input_uri[6:])
        elif self.protocol == 'video':
            pipeline = 'filesrc location=%s ! decodebin ! ' % self.input_uri
        elif self.protocol == 'webcam':
            pipeline = 'v4l2src device=%s ! video/x-raw ! ' % (self.input_uri)
        elif self.protocol == 'rtsp':
            pipeline = 'rtspsrc location=%s latency=0 ! capsfilter caps=application/x-rtp,media=video ! decodebin ! ' % self.input_uri
        elif self.protocol == 'http':
            pipeline = 'souphttpsrc location=%s is-live=true ! decodebin ! ' % self.input_uri
        return pipeline + cvt_pipeline

    @staticmethod
    def _parse_uri(uri):
        result = urlparse(uri)
        if result.scheme == 'csi':
            protocol = 'csi'
        elif result.scheme == 'rtsp':
            protocol = 'rtsp'
        elif result.scheme == 'http':
            protocol = 'http'
        else:
            if '/dev/video' in result.path:
                protocol = 'webcam'
            else:
                protocol = 'video'
        return protocol


class StreamerV2(object):
    def __init__(self, input_uri, width=None, height=None, max_queue_size=1, frame_skip=0, preprocess=None):
        super(StreamerV2, self).__init__()

        self.input_uri = input_uri
        self.protocol = self._parse_uri(self.input_uri)
        self.width = width
        self.height = height

        Gst.init(sys.argv)
        self.pipeline = Gst.parse_launch(self.gst_cap_pipeline())
        self.sink = self.pipeline.get_by_name("sink")
        self.set_callbacks()

        assert isinstance(max_queue_size, int)
        self.max_queue_size = max_queue_size
        self.queue = deque([])

        self.frame_skip = frame_skip
        self.preprocess = preprocess
        self.exit_event = Event()
        self.cond = Condition()
        self.thread = Thread(target=self.read_input_uri, name='Streamer')
        self.pipeline.set_state(Gst.State.PLAYING)
        self.thread.start()

    def set_callbacks(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call)

    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("pipeline ended")
            self.queue.clear()
            self.pipeline.set_state(Gst.State.NULL)
            sys.exit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error:\n{}\nAdditional debug info:\n{}\n".format(err, debug))
            self.queue.clear()
            self.pipeline.set_state(Gst.State.NULL)
            sys.exit()
        else:
            pass
        return True

    def pull_frame(self):
        try:
            sample = self.sink.pull_sample()
            caps_format = sample.get_caps().get_structure(0)  # Gst.Structure
            width, height = caps_format.get_value('width'), caps_format.get_value('height')
            buffer = sample.get_buffer()  # Gst.Buffer
            frame = ndarray(shape=(height, width, 3), dtype=uint8, buffer=buffer.extract_dup(0, buffer.get_size()))
            return True, frame
        except:
            return False, None

    def read_input_uri(self):
        counter = 0
        while not self.exit_event.is_set():
            ret, frame = self.pull_frame()
            counter += 1
            with self.cond:
                if not ret:
                    self.exit_event.set()
                    self.cond.notify()
                    break
                if counter % (self.frame_skip + 1) == 0:
                    counter = 0
                    if self.preprocess:
                        frame = self.preprocess(frame)
                        if frame:
                            self.queue.append(frame)
                    else:
                        self.queue.append(frame)
                    if self.max_queue_size > 0:
                        while len(self.queue) > self.max_queue_size:
                            self.queue.popleft()
                    self.cond.notify()

    def read_last(self):
        with self.cond:
            while len(self.queue) == 0 and not self.exit_event.is_set():
                self.cond.wait()
            if len(self.queue) == 0 and self.exit_event.is_set():
                return False, None
            frame = self.queue.pop()
            self.cond.notify()
        frame = resize(frame, width=self.width, height=self.height)
        return True, frame

    def read_first(self):
        with self.cond:
            while len(self.queue) == 0 and not self.exit_event.is_set():
                self.cond.wait()
            if len(self.queue) == 0 and self.exit_event.is_set():
                return False, None
            frame = self.queue.popleft()
            self.cond.notify()
        frame = resize(frame, width=self.width, height=self.height)
        return True, frame

    def release(self):
        with self.cond:
            self.exit_event.set()
            self.cond.notify()
        self.thread.join()
        self.queue.clear()
        self.pipeline.set_state(Gst.State.NULL)

    def gst_cap_pipeline(self):
        if self.protocol == 'csi':
            pipeline = 'nvarguscamerasrc sensor_id=%s ! video/x-raw(memory:NVMM), format=NV12 ! ' % (
                self.input_uri[6:])
        elif self.protocol == 'video':
            pipeline = 'filesrc location=%s ! decodebin ! ' % self.input_uri
        elif self.protocol == 'webcam':
            pipeline = 'v4l2src device=%s ! video/x-raw ! ' % (self.input_uri)
        elif self.protocol == 'rtsp':
            pipeline = 'urisourcebin buffer-size=4096 uri=%s ! decodebin ! videoconvert ! video/x-raw, format=BGR ! ' % self.input_uri
        elif self.protocol == 'http':
            pipeline = 'souphttpsrc location=%s is-live=true ! decodebin ! ' % self.input_uri
        return pipeline + 'videoconvert ! appsink name=sink sync=false'

    @staticmethod
    def _parse_uri(uri):
        result = urlparse(uri)
        if result.scheme == 'csi':
            protocol = 'csi'
        elif result.scheme == 'rtsp':
            protocol = 'rtsp'
        elif result.scheme == 'http':
            protocol = 'http'
        else:
            if '/dev/video' in result.path:
                protocol = 'webcam'
            else:
                protocol = 'video'
        return protocol


class StreamerV3(object):
    def __init__(self, input_uri, width=None, height=None):
        super(StreamerV3, self).__init__()
        self.input_uri = input_uri
        self.protocol = self._parse_uri(self.input_uri)
        self.width = width
        self.height = height

        Gst.init()
        self.pipeline = Gst.parse_launch(self.gst_cap_pipeline())
        self.set_callbacks()

    def capture(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def set_callbacks(self):
        # element = self.pipeline.get_by_name("sink")
        # element.connect("new-sample", self.on_buffer)
        # pad = element.get_static_pad("sink")
        # pad.add_probe(Gst.PadProbeType.BUFFER, self.pad_probe_callback)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call)

    def pull_frame(self):
        try:
            sample = self.sink.pull_sample()
            caps_format = sample.get_caps().get_structure(0)  # Gst.Structure
            width, height = caps_format.get_value('width'), caps_format.get_value('height')
            buffer = sample.get_buffer()  # Gst.Buffer
            frame = ndarray(shape=(height, width, 3), dtype=uint8, buffer=buffer.extract_dup(0, buffer.get_size()))
            return True, frame
        except:
            return False, None

    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("pipeline ended")
            self.pipeline.set_state(Gst.State.NULL)
            sys.exit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error:\n{}\nAdditional debug info:\n{}\n".format(err, debug))
            self.pipeline.set_state(Gst.State.NULL)
            sys.exit()
        else:
            pass
        return True

    def on_buffer(self, sink):
        sample = sink.emit("pull-sample")  # Gst.Sample
        caps_format = sample.get_caps().get_structure(0)  # Gst.Structure
        width, height = caps_format.get_value('width'), caps_format.get_value('height')
        buffer = sample.get_buffer()  # Gst.Buffer
        image = ndarray(shape=(height, width, 3), dtype=uint8, buffer=buffer.extract_dup(0, buffer.get_size()))
        return False

    def pad_probe_callback(self, pad: Gst.Pad, info: Gst.PadProbeInfo):
        # Extract the width and height info from the pad's caps
        caps = pad.get_current_caps()
        height = caps.get_structure(0).get_value("height")
        width = caps.get_structure(0).get_value("width")
        # Get the actual data
        buffer = info.get_buffer()
        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            raise RuntimeError("Could not map buffer data!")
        image = ndarray(shape=(height, width, 3), dtype=uint8, buffer=buffer.extract_dup(0, buffer.get_size()))
        buffer.unmap(map_info)
        return Gst.PadProbeReturn.OK

    def release(self):
        self.pipeline.set_state(Gst.State.NULL)

    def gst_cap_pipeline(self):
        if self.protocol == 'csi':
            pipeline = 'nvarguscamerasrc sensor_id=%s ! video/x-raw(memory:NVMM), format=NV12 ! ' % (
                self.input_uri[6:])
        elif self.protocol == 'video':
            pipeline = 'filesrc location=%s ! decodebin ! ' % self.input_uri
        elif self.protocol == 'webcam':
            pipeline = 'v4l2src device=%s ! video/x-raw ! ' % (self.input_uri)
        elif self.protocol == 'rtsp':
            pipeline = 'urisourcebin buffer-size=4096 uri=%s ! decodebin ! videoconvert ! video/x-raw, format=BGR ! ' % self.input_uri
        elif self.protocol == 'http':
            pipeline = 'souphttpsrc location=%s is-live=true ! decodebin ! ' % self.input_uri
        return pipeline + 'videoconvert ! appsink name=sink sync=false'

    @staticmethod
    def _parse_uri(uri):
        result = urlparse(uri)
        if result.scheme == 'csi':
            protocol = 'csi'
        elif result.scheme == 'rtsp':
            protocol = 'rtsp'
        elif result.scheme == 'http':
            protocol = 'http'
        else:
            if '/dev/video' in result.path:
                protocol = 'webcam'
            else:
                protocol = 'video'
        return protocol
