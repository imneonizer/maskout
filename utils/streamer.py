import base64
import cv2
import numpy as np
import zmq
import threading
import time

class StreamServer:
    def __init__(self, host="localhost", zmq_port=5555):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.PUB)

        # limit publisher buffer size
        self.footage_socket.setsockopt(zmq.SNDHWM, 2)

        self.host = host
        self.zmq_port = zmq_port
        self.footage_socket.bind('tcp://{}:{}'.format(self.host, self.zmq_port))
    
    def send(self, frame):
        try:
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            self.footage_socket.send(jpg_as_text)
        except Exception as e:
            print(e)