from msgpack import packb, Unpacker

from aiomsgpackrpc.client import MsgPackRpcError
from aiomsgpackrpc.client.sync import Server as BaseServer


class Server(BaseServer):

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
