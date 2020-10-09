import base64
import cv2
import numpy as np
import zmq
import threading
import time

class StreamServer:
    def __init__(self, host="localhost", port=5555):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.PUB)
        self.host = host
        self.port = port
        self.footage_socket.connect('tcp://{}:{}'.format(self.host, self.port))
    
    def send(self, frame):
        try:
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            self.footage_socket.send(jpg_as_text)
        except Exception as e:
            print(e)

class StreamClient:
    def __init__(self, host="*", port=5555, width=1280, height=720):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.SUB)
        self.host = host
        self.port = port
        self.footage_socket.bind('tcp://{}:{}'.format(self.host, self.port))
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

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
                cap = self.VideoCapture("rtsp://localhost:8554/ds-test", 1280, 720, 200)
            
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