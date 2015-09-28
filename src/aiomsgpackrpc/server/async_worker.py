import asyncio

from msgpack import Unpacker, packb

from aiomsgpackrpc.server import MsgpackProtocol


@asyncio.coroutine
def one_shot_rpc(msg, host, port, loop):
    f = asyncio.Future()
    asyncio.ensure_future(loop.create_connection(
        lambda: SlaveClientProtocol(msg, f, loop), host, port), loop=loop)
    return f


class SlaveClientProtocol(asyncio.Protocol):

    def __init__(self, msg, future, loop):
        self.msg = msg
        self.future = future
        self._loop = loop
        self.packer = Unpacker()

    def connection_made(self, transport):
        transport.write(packb(self.msg))

    def data_received(self, data):
        self.packer.feed(data)
        for msg in self.packer:
            self.future.set_result(msg)

    def connection_lost(self, exc):
        if not self.future.done():
            self.future.set_exception(Exception("Connection lost"))


class AppDispatcher(dict):

    def __init__(self, slave, loop):
        self._slave = slave
        self.loop = loop

    def make_handler(self):
        return MsgpackDispatcherProtocol(self._slave, self.loop)


class MsgpackDispatcherProtocol(MsgpackProtocol):

    def __init__(self, slave, loop):
        self._slave = slave
        self.packer = Unpacker()
        self.loop = loop

    def write_slave(self, msg):
        f = asyncio.Future()
        coro = self.loop.create_connection(lambda: SlaveClientProtocol(msg, f,
                                                                       self.loop),
                                           *self.slave)
        return f

    def routing(self, msg):
        # FIXME should not unpack and repack
        r = yield from one_shot_rpc(msg, self._slave[0], self._slave[1],
                                    self.loop)
        self.transport.write(packb(r))



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = AppDispatcher(('127.0.0.1', 8000), loop)

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
