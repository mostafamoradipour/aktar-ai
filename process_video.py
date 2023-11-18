from time import time
import numpy as np
import subprocess
import cv2


def _gst_write_pipeline(output_uri):
    gst_elements = str(subprocess.check_output('gst-inspect-1.0'))
    # use hardware encoder if found
    if 'omxh264enc' in gst_elements:
        h264_encoder = 'omxh264enc preset-level=2'
    elif 'x264enc' in gst_elements:
        h264_encoder = 'x264enc pass=4'
    else:
        raise RuntimeError('GStreamer H.264 encoder not found')
    pipeline = (
        'appsrc ! autovideoconvert ! %s ! qtmux !  filesinklocation=%s '
        % (
            h264_encoder,
            output_uri
        )
    )
    print(pipeline)
    return pipeline


video_pths = ['rtsp://192.168.1.103:554/user=admin&password=&channel=2&stream=0.sdp?real_stream--rtp-caching=800']

fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter("out.avi", fourcc, 12.0, (1920, 540))
# out = cv2.VideoWriter(_gst_write_pipeline("/mnt/storage/projects/Aktar/Aktar-develop/cam1.mp4"), cv2.CAP_GSTREAMER, 0, 12.0, (1280, 720), True)

vids = []
for pth in video_pths:
    vids.append(cv2.VideoCapture(pth))

frame_count = 0

while True:
    start_time = time()
    frames = []
    for vid in vids:
        st = time()
        ret, frame = vid.read()
        print(time() - st)
        vidtime = vid.get(cv2.CAP_PROP_POS_MSEC)/1000
        # print(vidtime)
        if not ret:
            break
        # frame = cv2.resize(frame, (960, 540))
        frames.append(frame)
    if ret:
        frame_count += 1
        # if frame_count >= 3960 and frame_count <= (3983 + 53):
        #     continue
        # if frame_count <= 250:
        #     continue
        # if frame_count > 240:
        #     break
        # out_frame = np.concatenate((np.concatenate(frames[:2]), np.concatenate(frames[2:])), axis=1)
        # out_frame = np.concatenate((frames[0], frames[1]), axis=1)
        # out_frame = frames[0]
        # print(out_frame.shape)
        # out.write(out_frame)
        # print(frame_count)
    else:
        break
for vid in vids:
    vid.release()

# out.release()
