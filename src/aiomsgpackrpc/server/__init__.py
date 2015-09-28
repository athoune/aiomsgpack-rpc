import asyncio

from msgpack import Unpacker, packb


class App(dict):

    def make_handler(self):
        return MsgpackProtocol(self)

    def method(self, f, name=None):
        if name is None:
            name = f.__name__
        self[bytes(name, 'utf8')] = f


@asyncio.coroutine
def response(id, transport, coro, args):
    r = yield from coro(*args)
    transport.write(packb([1, id, None, r]))


def assert_request(msg):
    assert type(msg) == list
    assert len(msg) >= 4
    assert 0 == msg[0]
    assert type(msg[1]) == int


class MsgpackProtocol(asyncio.Protocol):

    def __init__(self, routes):
        self.__routes = routes
        self.packer = Unpacker()

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.transport.write(packb([2, 'peername', peername]))

    def data_received(self, data):
        self.packer.feed(data)
        for msg in self.packer:
            assert_request(msg)
            self.routing(msg)

    def routing(self, cmd):
        assert cmd[2] in self.__routes
        t = asyncio.ensure_future(response(cmd[1], self.transport,
                                           self.__routes[cmd[2]], cmd[3]))

    def eof_received(self):
        return True


if __name__ == '__main__':

    app = App()

    @app.method
    @asyncio.coroutine
    def add(a, b):
        print(a, "+", b)
        yield from asyncio.sleep(a+b)
        return a+b

    loop = asyncio.get_event_loop()
    coro = loop.create_server(app.make_handler, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
