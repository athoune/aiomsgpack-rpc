import sys
sys.path.append('src')

from msgpack import Unpacker, packb

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8000))
s.sendall(packb([0, 1, "add", (1, 2)]))

u = Unpacker()
while True:
    data = s.recv(2048)
    if data is not None:
        u.feed(data)
        for resp in u:
            print(resp)
        break
