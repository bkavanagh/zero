import zmq
import random
import pyudev
from uuid import uuid4
import websocket
try:
    import thread
except ImportError:  #TODO use Threading instead of _thread in python3
    import _thread as thread
import time
import sys

host = 'ws://localhost:8888'

class WebsocketClient(object):

    def __init__(self):
        self.ws = None
        self.socket = None

    def create_ws(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(host,
                            on_message = self.on_ws_message,
                            on_error = self.on_ws_error,
                            on_close = self.on_ws_close)
        self.ws.on_open = self.on_ws_open
        self.ws.run_forever()

    def on_ws_message(self, ws, message):
        if self.socket:
            self.send_to_charger(message)


    def on_ws_error(self, ws, error):
        print(error)


    def on_ws_close(self, ws):
        print("### closed ###")


    def on_ws_open(self, ws):
        self.open_socket_con()

    def open_socket_con(self):
        port = "5559"
        context = zmq.Context()
        print "Connecting to server..."
        self.socket = context.socket(zmq.REQ)
        self.socket.connect ("tcp://localhost:%s" % port)

    def send_to_charger(self, msg):
        self.socket.send("{}:{}".format(msg, str(uuid4())))
        reply = self.socket.recv()
        self.send_to_server(reply)

    def send_to_server(self, reply):
        self.ws.send(reply)

if __name__ == "__main__":
    w = WebsocketClient()
    w.create_ws()