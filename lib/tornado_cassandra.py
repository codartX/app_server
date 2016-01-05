from cassandra.cluster import OperationTimedOut

from tornado.concurrent import Future

class TornadoCassandra(object):

    def __init__(self, session, ioloop):
        self._session = session
        self._ioloop = ioloop

    def execute(self, *args, **kwargs):
        tornado_future = Future()
        cassandra_future = self._session.execute_async(*args, **kwargs)
        self._ioloop.add_callback(
            self._callback, cassandra_future, tornado_future)
        return tornado_future

    def _callback(self, cassandra_future, tornado_future):
        try:
            # should spend just about no time blocking.
            result = cassandra_future.result(timeout=0)
        except OperationTimedOut:
            return self._ioloop.add_callback(
                self._callback, cassandra_future, tornado_future)
        except Exception, exc:
            return tornado_future.set_exception(exc)
        tornado_future.set_result(result)
