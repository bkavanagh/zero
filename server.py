__author__ = 'brendan'
import zmq
import time
import sys
import random
from uuid import uuid4
port = "5560"
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:%s" % port)
server_id = random.randrange(1,10005)
while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    time.sleep(1)
    socket.send("Charger Client Reply {}".format(str(uuid4())))
