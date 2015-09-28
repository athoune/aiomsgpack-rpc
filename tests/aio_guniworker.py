import sys
sys.path.append('src')

import asyncio

from aiomsgpackrpc.server import one_shot_rpc


loop = asyncio.get_event_loop()
coro = one_shot_rpc([0, 1, b"add", (1, 2)], '127.0.0.1', 8000, loop)
r = loop.run_until_complete(coro)
print("complete", r)
loop.close()
