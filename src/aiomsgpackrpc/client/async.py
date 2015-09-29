import asyncio

from msgpack import Unpacker, packb


class Server:

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.proxy = Proxy(self)
        self.loop = loop
        self.transfert = None
        self.protocol = ClientProtocol()
        self.queries = asyncio.Queue()

    @asyncio.coroutine
    def start(self):
        self._action_loop = True
        self._action_task = asyncio.ensure_future(self._work(), loop=self.loop)

    @asyncio.coroutine
    def lazy_connection(self):
        if self.transfert is None:
            self.transfert, _ = yield from self.loop.create_connection(
                lambda: self.protocol, self.host, self.port)

    def request(self, name, args, f):
        print('request')
        self.queries.put_nowait((name, args, f))

    def _work(self):
        while self._action_loop:
            name, args, f = yield from self.queries.get()
            if not f.cancelled():
                yield from self.lazy_connection()
                self.protocol.request(name, args, f)
        print("Stop working")

    @asyncio.coroutine
    def stop(self):
        self._action_loop = False
        yield from self._action_task


class Proxy:

    def __init__(self, server):
        self._server = server

    def __getattr__(self, name):
        return Method(self._server, name)


class Method(object):

    def __init__(self, server, name):
        self._server = server
        self._name = name

    def __call__(self, *args):
        f = asyncio.Future()
        self._server.request(self._name, args, f)
        return f


class ClientProtocol(asyncio.Protocol):

    def __init__(self):
        self._cpt = -1
        self.packer = Unpacker()
        self._responses = dict()

    def connection_made(self, transport):
        print("connected")
        self.transport = transport

    def request(self, name, args, f):
        print("send request")
        self._cpt += 1
        self._responses[self._cpt] = f
        self.transport.write(packb([0, self._cpt, name, args]))


    def data_received(self, data):
        self.packer.feed(data)
        for msg in self.packer:
            if msg[0] == 1:
                self._responses[msg[1]].set_result(msg)

    def connection_lost(self, exc):
        pass
