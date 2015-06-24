import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.callback = PeriodicCallback(self.send_hello, 10)
        self.callback.start()

    def send_hello(self):
        self.write_message('Websocket')

    def on_message(self, message):
        print 'Recieved Websocket Reply {}'.format(message)

    def on_close(self):
        self.callback.stop()

application = tornado.web.Application([
    (r'/', WSHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()