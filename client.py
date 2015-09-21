import socket

from msgpack import packb, Unpacker

HOST, PORT = 'localhost', 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
b = packb([0, 1, u'add', [1, 2]])
s.sendall(b)
b = packb([0, 2, u'add', [1, 0]])
s.sendall(b)

u = Unpacker()
while True:
    data = s.recv(1024)
    u.feed(data)
    for r in u:
        print(r)
s.close()
