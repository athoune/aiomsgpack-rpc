Aiomsgpack-rpc
==============

[msgpack-rpc](https://github.com/msgpack-rpc/msgpack-rpc/blob/master/spec.md) server built with asyncio.

This connected protocol doesn't use the request-response pattern,
you send many requests on the wire, and responses came back when they are ready,
in any order. Server can send message, a response without its request.

Life is short, don't sum latencies, parralize all the things! embrace the async revolution!

Server side
-----------

### Async pattern

Pure asyncio worker, useful with IO bound tasks.

### Sync pattern

Gunicorn are used as a pool of workers, behind an async multiplexer.

Workers can use python 2.7, Pypy or Python 3.4+

Useful with legacy code or CPU bound works (Numpy and its friends).

Client side
-----------

### Async pattern

Pure asyncio client.

### Sync client

Specific future pattern implementation, with a sequentiel connection.

Doc
---

The tests folder contains examples.

Status
------

Dangerous POC.

Licence
-------

3 Terms BSD licence, © 2015 Mathieu Lecarme.
