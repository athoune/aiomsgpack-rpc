from gunicorn.app.base import Application
from gunicorn.config import Config
from gunicorn.workers.sync import SyncWorker
from gunicorn.arbiter import Arbiter

from msgpack import Unpacker, packb


class SocketApplication(Application):

    def init(self, parser, opts, args):
        pass

    def wsgi(self):
        return None


class Worker(SyncWorker):
    _methods = dict()

    def handle(self, listener, client, addr):
        u = Unpacker()
        while True:
            u.feed(client.recv(4096))
            self.notify()
            for msg in u:
                _, msgid, method, params = msg
                try:
                    r = self.cfg.methods[method](*params)
                except Exception as e:
                    client.sendall(packb([1, msgid, e.message, None]))
                else:
                    client.sendall(packb([1, msgid, None, r]))
                finally:
                    self.notify()


if __name__ == '__main__':
    import time

    def add(a, b):
        print(a, "+", b)
        time.sleep(a+b)
        return a+b

    app = SocketApplication()
    app.cfg.methods = dict(add=add)

    arbiter = Arbiter(app)

    arbiter.worker_class = Worker
    arbiter.run()
