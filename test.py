from multiprocessing import Process
import pyshine as ps
import cv2


HTML = """
<html>
<head>
<title>PyShine Live Streaming</title>
</head>

<body>
<center><h1> PyShine Live Streaming Multiple videos </h1></center>
<center><img src="http://192.168.1.100:9000/stream.mjpg" width='360' height='240' autoplay playsinline></center>
<br>
<center><img src="http://192.168.1.100:9001/stream.mjpg" width='360' height='240' autoplay playsinline></center>
</body>
</html>
"""


def main1():
    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps, HTML)
    address = ('192.168.1.100', 9000)  # Enter your IP address
    try:
        StreamProps.set_Mode(StreamProps, 'cv2')
        # replace 0 (webcam id) with the path of your .mp4 video file
        # capture = cv2.VideoCapture("rtsp://192.168.1.101:554/user=admin&password=&channel=1&stream=0.sdp?real_stream--rtp-caching=800")
        gst_string = "rtspsrc location=rtsp://192.168.1.101:554/user=admin&password=&channel=1&stream=1.sdp?real_stream--rtp-caching=800 latency=0 ! capsfilter caps=application/x-rtp,media=video ! decodebin ! nvvidconv interpolation-method=5 ! video/x-raw, format=BGRx ! videoconvert ! appsink sync=false"
        capture = cv2.VideoCapture(gst_string, cv2.CAP_GSTREAMER)
        # capture.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # capture.set(cv2.CAP_PROP_FPS, 30)
        StreamProps.set_Capture(StreamProps, capture)
        StreamProps.set_Quality(StreamProps, 90)
        server = ps.Streamer(address, StreamProps)
        print('Server started at', 'http://'+address[0]+':'+str(address[1]))
        server.serve_forever()
        print('done')

    except KeyboardInterrupt:
        capture.release()
        server.socket.close()


def main2():
    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps, HTML)
    address = ('192.168.1.100', 9001)  # Enter your IP address
    try:
        StreamProps.set_Mode(StreamProps, 'cv2')
        # replace 1 (webcam id) with the path of your .mp4 for video file
        # capture = cv2.VideoCapture("rtsp://192.168.1.101:554/user=admin&password=&channel=2&stream=0.sdp?real_stream--rtp-caching=800")
        gst_string = "rtspsrc location=rtsp://192.168.1.101:554/user=admin&password=&channel=2&stream=1.sdp?real_stream--rtp-caching=800 latency=0 ! capsfilter caps=application/x-rtp,media=video ! decodebin ! nvvidconv interpolation-method=5 ! video/x-raw, format=BGRx ! videoconvert ! appsink sync=false"
        capture = cv2.VideoCapture(gst_string, cv2.CAP_GSTREAMER)
        # capture.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # capture.set(cv2.CAP_PROP_FPS, 30)
        StreamProps.set_Capture(StreamProps, capture)
        StreamProps.set_Quality(StreamProps, 90)
        server = ps.Streamer(address, StreamProps)
        print('Server started at', 'http://'+address[0]+':'+str(address[1]))
        server.serve_forever()
        print('done')

    except KeyboardInterrupt:
        capture.release()
        server.socket.close()


if __name__ == '__main__':
    p1 = Process(target=main1)
    p1.start()
    p2 = Process(target=main2)
    p2.start()
