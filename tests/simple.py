"""
Launch the server :
    python -m aiomsgpackrpc.server

Test it:
    python tests/simple.py
"""
import sys
sys.path.append('src')

from aiomsgpackrpc.client.sync.simple import Server


if __name__ == '__main__':
    s = Server('localhost', 8888)
    p = s.proxy
    print(p.add(1, 2))
