import asyncio
from . import App

app = App()

@app.method
@asyncio.coroutine
def add(a, b):
    print(a, "+", b)
    r = a+b
    yield from asyncio.sleep(r)
    print("=", r)
    return r

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
