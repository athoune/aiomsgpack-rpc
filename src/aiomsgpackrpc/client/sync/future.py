import socket
import weakref

from msgpack import packb, Unpacker


class Server(object):

    def __init__(self, host, port):
        self._cpt = -1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self.proxy = Proxy(self)
        self._waiting = 0
        self._responses = dict()
        self._cb = dict()

    def call(self, name, args):
        self._cpt += 1
        self._socket.sendall(packb([0, self._cpt, name, args]))
        self._waiting += 1
        return self._cpt

    def close(self):
        self._socket.close()

    def notification(self, f, name=None):
        if name is None:
            name = f.func_name
        self._cb[name] = f
        return f

    def responses(self):
        u = Unpacker()
        while self._waiting > 0:
            data = self._socket.recv(2048)
            u.feed(data)
            for r in u:
                if r[0] == 2:
                    if r[1] in self._cb:
                        self._cb[r[1]](*r[2])
                    else:
                        print("Unknown notification:", r[1], r[2])
                else:
                    self._waiting -= 1
                    yield r


def as_completed(fs):
    s = fs[0]._server
    for r in s.responses():
        f = s._responses[r[1]]
        f.set_result(r[3])
        f.set_exception(r[2])
        yield f


class Method(object):

    def __init__(self, server, name):
        self._server = server
        self._name = name

    def __call__(self, *args):
        f = Future(self._server, self._server.call(self._name, args))
        self._server._responses[f._id] = weakref.proxy(f)
        return f


class Future(object):
    _done = False
    _result = None
    _exception = None
    _cb = None

    def __init__(self, server, id):
        self._server = server
        self._id = id

    def result(self):
        if self._exception is not None:
            raise self._exception
        return self._result

    def done(self):
        return self._done

    def add_done_callback(self, fn):
        self._cb = fn

    def set_result(self, result):
        self._result = result
        if not self._done and self._cb is not None:
            self._cb(self)
        self._done = True

    def set_exception(self, exception):
        self._exception = exception
        if not self._done and self._cb is not None:
            self._cb(self)
        self._done = True

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other._id

    def __del__(self):
        del self._server._responses[self._id]


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
