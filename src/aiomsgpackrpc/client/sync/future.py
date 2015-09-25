import socket

from msgpack import packb, Unpacker


class Server(object):

    def __init__(self, host, port):
        self._cpt = -1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self.proxy = Proxy(self)

    def call(self, name, args):
        self._cpt += 1
        self._socket.sendall(packb([0, self._cpt, name, args]))
        return self._cpt

    def close(self):
        self._socket.close()

    def __iter__(self):
        u = Unpacker()
        while True:
            data = self._socket.recv(2048)
            u.feed(data)
            for r in u:
                yield r


class Method(object):

    def __init__(self, server, name):
        self._server = server
        self._name = name

    def __call__(self, *args):
        return Future(self._server.proxy, self._server.call(self._name, args))


class Future(object):

    def __init__(self, proxy, id):
        self._proxy = proxy
        self._id = id


class Proxy(object):

    def __init__(self, server):
        self.__server = server

    def __getattr__(self, name):
        return Method(self.__server, name)


if __name__ == '__main__':
    server = Server('localhost', 8888)

    proxy = server.proxy

    proxy.add(1, 2)
    proxy.add(1, 0)

    n = 0
    for m in server:
        print(m)
        if m[0] == 1:
            n+=1
        if n == 2:
            break

    server.close()
