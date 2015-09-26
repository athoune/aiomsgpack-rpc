import sys
sys.path.append('src')

from aiomsgpackrpc.client.sync.future import Server, as_completed


if __name__ == '__main__':
    s = Server('localhost', 8888)

    @s.notification
    def peername(ip, port):
        print("Connection from IP: {} Port: {}".format(ip, port))

    p = s.proxy
    f1 = p.add(1, 2)
    print("f1", f1)
    f2 = p.add(1, 0)
    print("f2", f2)
    for r in as_completed([f1, f2]):
        print(r.result())
        assert r == f1 or r == f2
    assert len(s._responses) == 2
    del f1
    assert len(s._responses) == 1
    del f2
    assert len(s._responses) == 0
