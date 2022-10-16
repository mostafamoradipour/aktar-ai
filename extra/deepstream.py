from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
from gi.repository import GLib, Gst
from common.FPS import PERF_DATA
from ctypes import *
import argparse
import math
import sys
import gi
sys.path.append('../')
gi.require_version('Gst', '1.0')


no_display = False
silent = False
file_loop = False
perf_data = None

MAX_DISPLAY_LEN = 64
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 4000000
TILED_OUTPUT_WIDTH = 1920
TILED_OUTPUT_HEIGHT = 1080
GST_CAPS_FEATURES_NVMM = "memory:NVMM"


def cb_newpad(decodebin, decoder_src_pad, data):
    print("In cb_newpad\n")
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    print("gstname=", gstname)
    if (gstname.find("video") != -1):
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        print("features=", features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write(
                    "Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(
                " Error: Decodebin did not pick nvidia decoder plugin.\n")


def decodebin_child_added(child_proxy, Object, name, user_data):
    print("Decodebin child added:", name, "\n")
    if (name.find("decodebin") != -1):
        Object.connect("child-added", decodebin_child_added, user_data)

    if "source" in name:
        source_element = child_proxy.get_by_name("source")
        if source_element.find_property('drop-on-latency') != None:
            Object.set_property("drop-on-latency", True)


def create_source_bin(index, uri):
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name = "source-bin-%02d" % index
    print(bin_name)
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    if file_loop:
        # use nvurisrcbin to enable file-loop
        uri_decode_bin = Gst.ElementFactory.make(
            "nvurisrcbin", "uri-decode-bin")
        uri_decode_bin.set_property("file-loop", 1)
    else:
        uri_decode_bin = Gst.ElementFactory.make(
            "uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri", uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(
        Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin


def streamer(args):
    global perf_data
    perf_data = PERF_DATA(len(args))

    number_sources = len(args)

    # Standard GStreamer initialization
    Gst.init(None)

    # Create gstreamer elements */
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    is_live = True

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    print("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    for i in range(number_sources):
        print("Creating source_bin ", i, " \n ")
        uri_name = args[i]
        # if uri_name.find("rtsp://") == 0:
        #     is_live = True
        source_bin = create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        pipeline.add(source_bin)
        padname = "sink_%u" % i
        sinkpad = streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    queue2 = Gst.ElementFactory.make("queue", "queue2")
    queue3 = Gst.ElementFactory.make("queue", "queue3")
    queue4 = Gst.ElementFactory.make("queue", "queue4")
    pipeline.add(queue1)
    pipeline.add(queue2)
    pipeline.add(queue3)
    pipeline.add(queue4)

    nvdslogger = None
    transform = None

    print("Creating tiler \n ")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    print("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    if no_display:
        print("Creating Fakesink \n")
        sink = Gst.ElementFactory.make("fakesink", "fakesink")
        sink.set_property('enable-last-sample', 0)
        sink.set_property('sync', 0)
    else:
        if (is_aarch64()):
            print("Creating transform \n ")
            transform = Gst.ElementFactory.make(
                "nvegltransform", "nvegl-transform")
            if not transform:
                sys.stderr.write(" Unable to create transform \n")
        print("Creating EGLSink \n")
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")

    if not sink:
        sys.stderr.write(" Unable to create sink element \n")

    if is_live:
        print("At least one of the sources is live")
        streammux.set_property('live-source', 1)

    streammux.set_property('width', 1920)
    streammux.set_property('height', 1080)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout', 4000000)

    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0*number_sources)/tiler_rows))
    tiler_rows, tiler_columns = 2, 2
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("qos", 0)

    print("Adding elements to Pipeline \n")
    if nvdslogger:
        pipeline.add(nvdslogger)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    if transform:
        pipeline.add(transform)
    pipeline.add(sink)

    print("Linking elements in the Pipeline \n")
    streammux.link(queue1)
    queue1.link(queue2)
    if nvdslogger:
        queue2.link(nvdslogger)
        nvdslogger.link(tiler)
    else:
        queue2.link(tiler)
    tiler.link(queue3)
    queue3.link(nvvidconv)
    nvvidconv.link(queue4)
    if transform:
        queue4.link(transform)
        transform.link(sink)
    else:
        queue4.link(sink)

    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # List the sources
    print("Now playing...")
    for i, source in enumerate(args):
        print(i, ": ", source)

    print("Starting pipeline \n")
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # cleanup
    print("Exiting app\n")
    pipeline.set_state(Gst.State.NULL)


def parse_args():
    parser = argparse.ArgumentParser(prog="deepstream_test_3",
                                     description="deepstream-test3 multi stream, multi model inference reference app")
    parser.add_argument(
        "-i",
        "--input",
        help="Path to input streams",
        nargs="+",
        metavar="URIs",
        default=["a"],
        required=True,
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        default=False,
        dest='no_display',
        help="Disable display of video output",
    )
    parser.add_argument(
        "--file-loop",
        action="store_true",
        default=False,
        dest='file_loop',
        help="Loop the input file sources after EOS",
    )
    parser.add_argument(
        "--disable-probe",
        action="store_true",
        default=False,
        dest='disable_probe',
        help="Disable the probe function and use nvdslogger for FPS",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        default=False,
        dest='silent',
        help="Disable verbose output",
    )
    # Check input arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    stream_paths = args.input
    global no_display
    global silent
    global file_loop
    no_display = args.no_display
    silent = args.silent
    file_loop = args.file_loop

    print(vars(args))
    return stream_paths


if __name__ == '__main__':
    stream_paths = parse_args()
    sys.exit(streamer(stream_paths))
