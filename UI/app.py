from flask import Flask, Response, render_template, send_file
from utils.streamer import StreamClient
import argparse

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/heat")
def heat_():
    return send_file("walking.jpg")

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(stream_client.generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--server", required=True,
        help="server ip address, to receive data from")
    ap.add_argument("-r", "--rtsp_port", type=int, default=8554,
        help="server rtsp port, used for receiving inference video")
    ap.add_argument("-z", "--zmq_port", type=int, default=5555,
        help="server zmq port, used for receiving heatmap data")
    ap.add_argument("-c", "--client", default="x86",
        help="['jetson', 'x86'], if running on jetson nvvideodecoder can be used to decode rtsp feed")
    ap.add_argument("-p", "--port", default=5000,
        help="port address to run client application")
    args = ap.parse_args()

    # stream_client = StreamClient(host=args.server, rtsp_port=args.rtsp_port, zmq_port=args.zmq_port, client=args.client)
    app.run(debug=True, host="0.0.0.0", port=5000)