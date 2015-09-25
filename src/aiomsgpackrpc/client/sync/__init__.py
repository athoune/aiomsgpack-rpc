import socket
from Queue import Queue


class Server(object):

    def __init__(self, host, port, max_events=500):
        self._cpt = -1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self.proxy = Proxy(self)
        self.events = Queue(maxsize=max_events)

    def close(self):
        self._socket.close()


class Proxy(object):

    def __init__(self, server):
        self.__server = server

    def __getattr__(self, name):
        return Method(self.__server, name)


class Method(object):

    def __init__(self, server, name):
        self._server = server
        self._name = name

    def __call__(self, *args):
        r = self._server.call(self._name, args)
        if r[2] is not None:
            raise MsgPackRpcError(r[2])
        return r[3]
