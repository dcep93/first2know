import base64
import datetime
import hashlib
import json
import io
import os
import queue
import random
import string
import threading
import time
import typing

from pydantic import BaseModel

from PIL import Image, ImageDraw

from . import firebase_wrapper
from . import secrets

TIMEOUT_SECONDS = 10.0


class Request(BaseModel):
    data_input: firebase_wrapper.DataInput
    evaluation: typing.Any


class Response(BaseModel):
    img_data: str
    evaluation: typing.Any
    md5: str


class Manager:
    def __init__(self, num_screenshotters):
        self.queue_in = queue.Queue(num_screenshotters)
        self.queues_out = queue.Queue(num_screenshotters)
        init_registers = [queue.Queue(1) for _ in range(num_screenshotters)]
        for register in init_registers:
            threading.Thread(
                target=lambda: self.run_screenshotter(self.queue_in, register),
            ).start()
        for register in init_registers:
            register.get()
            self.queues_out.put_nowait(register)

    @staticmethod
    def run_screenshotter(queue_in: queue.Queue, init_register: queue.Queue):
        screenshotter = Screenshot()
        init_register.put(None)
        while True:
            request, register = queue_in.get()
            response: Response = screenshotter.screenshot(request)
            register.put(response)

    def screenshot(self, request: Request) -> Response:
        register = self.queues_out.get()
        self.queue_in.put_nowait((request, register))
        response = register.get()
        self.queues_out.put_nowait(register)
        return response


# https://playwright.dev/python/docs/intro
class Screenshot:
    def __init__(self):
        from playwright.sync_api import sync_playwright as p  # type: ignore

        entered = p().__enter__()
        self.browser = entered.chromium.launch()

    def get_chain(
        self,
        payload: firebase_wrapper.DataInput,
        previous_evaluation: typing.Any,
    ):
        params = None \
            if payload.params is None \
            else dict(payload.params)
        return [
            (
                "context",
                lambda d: self.browser.new_context(),
            ),
            (
                "page",
                lambda d: d["context"].new_page(),
            ),
            (
                "set_extra_http_headers",
                lambda d: d["page"].set_extra_http_headers(params),
            ),
            (
                "goto",
                lambda d: d["page"].goto(payload.url),
            ),
            (
                "evaluation",
                lambda d: None
                if payload.evaluate is None else d["page"].evaluate(
                    payload.evaluate, previous_evaluation),
            ),
            (
                "img",
                lambda d: self.get_img(d, payload),
            ),
        ]

    def get_img(
        self,
        d: typing.Dict[str, typing.Any],
        payload: firebase_wrapper.DataInput,
    ) -> bytes:
        if payload.evaluation_to_img:
            evaluation = d.get("evaluation")
            binary_data = self.evaluation_to_img_bytes(evaluation)
        else:
            key = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(10))
            dest = f"screenshot_{key}.png"
            to_screenshot = d["page"] \
                if payload.selector is None \
                else d["page"].locator(payload.selector)
            to_screenshot.screenshot(path=dest)
            with open(dest, "rb") as fh:
                binary_data = fh.read()
            os.remove(dest)
        encoded = base64.b64encode(binary_data)
        return encoded

    def screenshot(self, request: Request) -> Response:
        s = time.time()
        chain = self.get_chain(request.data_input, request.evaluation)
        d = self.execute_chain(chain)
        encoded: bytes = d["img"]
        img_data = encoded.decode('utf-8')
        md5 = hashlib.md5(encoded).hexdigest()
        self.log(' '.join([
            f"{time.time() - s:.3f}s",
            f"{len(img_data)/1000}kb",
            datetime.datetime.now().strftime("%H:%M:%S.%f"),
        ]))
        return Response(
            img_data=img_data,
            evaluation=d.get("evaluation"),
            md5=md5,
        )

    def log(self, s: str):
        if secrets.Vars.is_local:
            print(s)

    def evaluation_to_img_bytes(self, evaluation: typing.Any) -> bytes:
        text = evaluation \
            if type(evaluation) is str \
            else json.dumps(evaluation, indent=1)
        width = 100
        height = 100
        img = Image.new('1', (width, height))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, fill=255)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def execute_chain(
        self,
        chain: typing.List[typing.Tuple[str, typing.Any]],
    ) -> typing.Dict[str, typing.Any]:
        rval = {}
        for i, c in chain:
            start = time.time()
            j = c(rval)
            if j is not None:
                rval[i] = j
            self.log(f"{i} {time.time() - start}")
        return rval
