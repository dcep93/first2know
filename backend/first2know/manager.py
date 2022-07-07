import queue
import threading
import typing

T = typing.TypeVar('T')
U = typing.TypeVar('U')
V = typing.TypeVar('V')


class Manager(typing.Generic[T, U, V]):
    def __init__(
        self,
        f: typing.Callable[[], T],
        g: typing.Callable[[T, U], V],
        num: int,
    ):
        self.num = num
        self.request_queue = queue.Queue(self.num)
        self.response_queues = queue.Queue(self.num)
        for _ in range(self.num):
            threading.Thread(target=lambda: self.init_runner(
                f,
                g,
                self.request_queue,
                self.response_queues,
            )).start()
        for _ in range(self.num):
            err = self.response_queues.get()
            if err is not None:
                raise err

    def close(self):
        for _ in range(self.num):
            self.request_queue.put_nowait(_CLOSING_REQUEST)

    @staticmethod
    def init_runner(
        f: typing.Callable[[], T],
        g: typing.Callable[[T, U], V],
        request_queue: queue.Queue,
        response_queues: queue.Queue,
    ):
        try:
            runner = f()
        except Exception as e:
            response_queues.put(e)
            return
        response_queues.put(None)
        while True:
            _request, register = request_queue.get()
            if _request is _CLOSING_REQUEST:
                break
            request: U = _request
            try:
                response: V = g(runner, request)
            except Exception as e:
                register.put((e, False))
                break
            register.put((response, True))

    def run(self, request: U) -> V:
        register = self.response_queues.get()
        self.request_queue.put_nowait((request, register))
        (response, is_successful) = register.get()
        if not is_successful:
            raise response
        self.response_queues.put_nowait(register)
        return response


class _ClosingRequest:
    pass


_CLOSING_REQUEST = _ClosingRequest()
