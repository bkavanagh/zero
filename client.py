__author__ = 'brendan'
import zmq
import sys
import random
import pyudev

con = pyudev.Context()
mon = pyudev.Monitor.from_netlink(con)


port = "5559"
context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)
client_id = random.randrange(1,10005)
#  Do 10 requests, waiting each time for a response
for action, device in mon:
    print "Sending request ", action,"..."
    socket.send ("Udev Device {} : {}".format(action, device))
    reply = socket.recv()