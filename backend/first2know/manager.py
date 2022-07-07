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
        num_runners: int,
    ):
        self.request_queue = queue.Queue(num_runners)
        self.response_queues = queue.Queue(num_runners)
        init_registers = [queue.Queue(1) for _ in range(num_runners)]
        for register in init_registers:
            threading.Thread(target=lambda: self.init_runner(
                f, g, self.request_queue, register), ).start()
        for register in init_registers:
            register.get()
            self.response_queues.put_nowait(register)

    @staticmethod
    def init_runner(
        f: typing.Callable[[], T],
        g: typing.Callable[[T, U], V],
        request_queue: queue.Queue,
        init_register: queue.Queue,
    ):
        runner: T = f()
        init_register.put(None)
        while True:
            _request, register = request_queue.get()
            request: U = _request
            response: V = g(runner, request)
            register.put(response)

    def run(self, request: U) -> V:
        register = self.response_queues.get()
        self.request_queue.put_nowait((request, register))
        response = register.get()
        self.response_queues.put_nowait(register)
        return response
