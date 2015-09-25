import socket
from Queue import Queue

from msgpack import packb, Unpacker
from aiomsgpackrpc.client import MsgPackRpcError


class Server(object):

    def __init__(self, host, port, max_events=500):
        self._cpt = -1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self.proxy = Proxy(self)
        self.events = Queue(maxsize=max_events)

    def call(self, name, args):
        self._cpt += 1
        self._socket.sendall(packb([0, self._cpt, name, args]))
        u = Unpacker()
        while True:
            data = self._socket.recv(2048)
            u.feed(data)
            for r in u:
                if r[0] == 2:
                    self.events.put(r)
                else:
                    return r

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
