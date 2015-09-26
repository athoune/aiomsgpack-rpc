import socket
from Queue import Queue


class Method(object):

    def __init__(self, server, name):
        self._server = server
        self._name = name

    def __call__(self, *args):
        r = self._server.call(self._name, args)
        if r[2] is not None:
            raise MsgPackRpcError(r[2])
        return r[3]


class Server(object):

    def __init__(self, host, port, max_events=500, method=Method):
        self._cpt = -1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self.proxy = Proxy(self, method)
        self.events = Queue(maxsize=max_events)

    def close(self):
        self._socket.close()


class Proxy(object):

    def __init__(self, server, method=Method):
        self._server = server
        self._method = method

    def __getattr__(self, name):
        return self._method(self._server, name)
