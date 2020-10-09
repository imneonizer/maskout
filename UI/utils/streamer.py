import base64
import cv2
import numpy as np
import zmq
import threading
import time

class StreamClient:
    def __init__(self, host="localhost", rtsp_port=8554, zmq_port=5555, width=1280, height=720, client="jetson"):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.SUB)
        self.host = host
        self.zmq_port = zmq_port
        self.footage_socket.connect('tcp://{}:{}'.format(self.host, self.zmq_port))
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        self.client = client
        self.rtsp_port = rtsp_port
        self.width = width
        self.height = height
        self.rtsp_frame = np.zeros((self.height, self.width, 3), np.uint8)
        self.heatmap = np.zeros((self.height, self.width, 3), np.uint8)
        
        threading.Thread(target=self.update_rtsp_frame).start()
        threading.Thread(target=self.update_heatmap).start()
    
    def VideoCapture(self, uri, width, height, latency):
        gst_str = ('rtspsrc location={} latency={} ! '
                'rtph264depay ! h264parse ! omxh264dec ! '
                'nvvidconv ! '
                'video/x-raw, width=(int){}, height=(int){}, '
                'format=(string)BGRx ! '
                'videoconvert ! appsink').format(uri, latency, width, height)

        return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
    
    def update_rtsp_frame(self):
        cap = None
        while True:
            if not cap:
                if self.client == "jetson":
                    cap = self.VideoCapture("rtsp://{}:{}/ds-test".format(self.host, self.rtsp_port), self.width, self.height, 200)
                else:
                    cap = cv2.VideoCapture("rtsp://{}:{}/ds-test".format(self.host, self.rtsp_port))
            
            success, frame = cap.read()
            if not success:
                cap = None
                time.sleep(0.5)

            if frame is not None:
                # print("rtsp_frame:", frame.shape)
                self.rtsp_frame = frame

    def update_heatmap(self):
        while True:
            heatmap = self.receive()
            if heatmap is not None:
                # print("heatmap:", heatmap.shape)
                self.heatmap = heatmap
    
    def receive(self):
        try:
            frame = self.footage_socket.recv_string()
            frame = base64.b64decode(frame)
            frame = np.frombuffer(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            return frame
        except Exception as e:
            print(e)

    def read(self):
        rtsp_frame = self.rtsp_frame.copy()
        heatmap = self.heatmap.copy()

        if rtsp_frame.shape != (self.height, self.width, 3):
            print("rtsp shape mismatch", rtsp_frame.shape)
            return

        if heatmap.shape != (self.height, self.width, 3):
            print("heatmap shape mismatch", heatmap.shape)
            return

        frame = cv2.addWeighted(self.rtsp_frame.copy(), 0.7, self.heatmap.copy(), 0.5, 0) 
        return frame

    def generate(self):
        while True:
            frame = self.read()
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')