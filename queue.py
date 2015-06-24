__author__ = 'brendan'
import zmq

def main():

    try:
        context = zmq.Context(1)
        # Socket facing websocket
        websocket_in = context.socket(zmq.XREP)
        websocket_in.bind("tcp://*:5559")
        # Socket facing charger client
        charger_client = context.socket(zmq.XREQ)
        charger_client.bind("tcp://*:5560")
        # Socket facing Udev listener
        udev_listener = context.socket(zmq.XREQ)
        udev_listener.bind("tcp://*:5561")

        zmq.device(zmq.QUEUE, websocket_in, charger_client)
        zmq.device(zmq.QUEUE, udev_listener, charger_client)
    except Exception, e:
        print e
        print "bringing down zmq device"
    finally:
        pass
        websocket_in.close()
        charger_client.close()
        udev_listener.close()
        context.term()

if __name__ == "__main__":
    main()