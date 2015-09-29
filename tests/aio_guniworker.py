"""
Test your worker with an async client.

    python -m aiomsgpackrpc.server.worker.guniworker

the client
    python tests/aio_guniworker.py
"""
import sys
sys.path.append('src')

import asyncio

from aiomsgpackrpc.server.async_worker import one_shot_rpc


loop = asyncio.get_event_loop()
coro = one_shot_rpc([0, 1, b"add", (1, 2)], '127.0.0.1', 8000, loop)
r = loop.run_until_complete(coro)
print("complete", r)
loop.close()
