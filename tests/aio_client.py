"""
Launch the server :
    python -m aiomsgpackrpc.server

Test it:
    python tests/aio_client.py
"""
import sys
sys.path.append('src')

import asyncio

from aiomsgpackrpc.client.async import Server

loop = asyncio.get_event_loop()
s = Server('localhost', 8888, loop)
loop.run_until_complete(s.start())
f1 = s.proxy.add(1, 2)
f2 = s.proxy.add(1, 0)
print(f1)
print(f2)
loop.run_until_complete(asyncio.wait([f1, f2]))
print(f1)
print(f2)
#loop.run_until_complete(s.stop())
loop.close()
