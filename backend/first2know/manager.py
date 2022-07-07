import queue
import threading
import typing

T = typing.TypeVar('T')
U = typing.TypeVar('U')
V = typing.TypeVar('V')


class Manager(typing.Generic[T, U, V]):
    def __init__(
        self,
        f: typing.Callable[[], typing.Callable[[U], V]],
        num: int,
    ):
        self.f = f
        self.num = num
        self.request_queue = queue.Queue(self.num)
        self.response_queues = queue.Queue(self.num)
        for _ in range(self.num):
            threading.Thread(target=self.init_runner).start()
        for _ in range(self.num):
            err = self.response_queues.get()
            if err is not None:
                raise err
        for _ in range(self.num):
            self.response_queues.put_nowait(queue.Queue(1))

    def close(self):
        for _ in range(self.num):
            self.request_queue.put_nowait((None, None))

    def init_runner(self):
        try:
            runner = self.f()
        except Exception as e:
            self.response_queues.put(e)
            return
        self.response_queues.put(None)
        while True:
            _request, register = self.request_queue.get()
            if register is None:
                break
            request: U = _request
            try:
                response: V = runner(request)
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
