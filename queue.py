__author__ = 'brendan'
import zmq

def main():

    try:
        context = zmq.Context(1)
        # Socket facing websocket
        websocket_in = context.socket(zmq.SUB)
        websocket_in.setsockopt(zmq.IDENTITY, 'websocket_in')
        websocket_in.bind("tcp://*:5559")

        charger_client = context.socket(zmq.PUB)
        charger_client.setsockopt(zmq.IDENTITY, 'charger_client')
        charger_client.bind("tcp://*:5560")


        zmq.device(zmq.QUEUE, websocket_in, charger_client)

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