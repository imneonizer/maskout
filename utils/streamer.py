import base64
import cv2
import numpy as np
import zmq

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
    def __init__(self, host="*", port=5555):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.SUB)
        self.host = host
        self.port = port
        self.footage_socket.bind('tcp://{}:{}'.format(self.host, self.port))
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
    
    def receive(self):
        try:
            frame = self.footage_socket.recv_string()
            frame = base64.b64decode(frame)
            frame = np.fromstring(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            return frame
        except Exception as e:
            print(e)