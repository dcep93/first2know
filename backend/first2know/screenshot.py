import asyncio
import base64
import datetime
import hashlib
import io
import json
import os
import time
import typing
import uuid

from pydantic import BaseModel

from PIL import Image, ImageDraw

from . import firebase_wrapper
from . import proxy
from . import secrets

import nest_asyncio

nest_asyncio.apply()

GOOD_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"  # noqa


class Request(BaseModel):
    data_input: firebase_wrapper.DataInput
    evaluation: typing.Any = None


class Response(BaseModel):
    img_data: str
    evaluation: typing.Any
    md5: str
    elapsed: float


# https://playwright.dev/python/docs/intro
class Screenshot:
    def __init__(self):
        self.id = str(uuid.uuid1())
        self.p, self.browser = asyncio.run(self.async_init())

    async def async_init(self) -> typing.Tuple[typing.Any, typing.Any]:
        from playwright.async_api import async_playwright as _p  # type: ignore # noqa

        p = _p()

        entered = await p.__aenter__()
        browser = await entered.chromium.launch()
        return p, browser

    async def close(self):
        await self.browser.close()
        await self.p.__aexit__()

    def __call__(self, request: Request) -> Response:
        s = time.time()
        chain = self.get_chain(request.data_input, request.evaluation)
        _d = self.execute_chain(chain)
        d = asyncio.run(_d)
        binary_data: bytes = d["img"]
        encoded = base64.b64encode(binary_data)
        img_data = encoded.decode('utf-8')
        md5 = hashlib.md5(encoded).hexdigest()
        e = time.time()
        elapsed = e - s
        self.log(' '.join([
            f"{elapsed:.3f}s",
            f"{len(img_data)/1000}kb",
            datetime.datetime.now().strftime("%H:%M:%S.%f"),
        ]))
        return Response(
            img_data=img_data,
            evaluation=d.get("evaluation"),
            md5=md5,
            elapsed=elapsed,
        )

    def log(self, s: str):
        if secrets.Vars.is_local:
            print(self.id, s)

    def get_chain(
        self,
        payload: firebase_wrapper.DataInput,
        previous_evaluation: typing.Any,
    ):
        params = {} \
            if payload.params is None \
            else dict(payload.params)

        if payload.user_agent_hack:
            params["user-agent"] = GOOD_USER_AGENT

        if payload.raw_proxy:
            return [
                (
                    "proxy_result",
                    lambda d: d.update({
                        "proxy_result":
                        proxy.proxy(
                            proxy.Request(url=payload.url, params=params))
                    }),
                ),
                (
                    "img",
                    lambda d: self.obj_to_img_bytes(d["proxy_result"]),
                ),
            ]
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

    async def execute_chain(
        self,
        chain: typing.List[typing.Tuple[str, typing.Any]],
    ) -> typing.Dict[str, typing.Any]:
        rval = {}
        for i, c in chain:
            start = time.time()
            j = c(rval)
            if j is not None:
                rval[i] = await j
            self.log(f"{i} {time.time() - start}")
        return rval

    async def get_img(
        self,
        d: typing.Dict[str, typing.Any],
        payload: firebase_wrapper.DataInput,
    ) -> bytes:
        if payload.evaluation_to_img:
            evaluation = d.get("evaluation")
            binary_data = self.obj_to_img_bytes(evaluation)
        else:
            dest = f"screenshot_{self.id}.png"
            if payload.selector is None:
                to_screenshot = d["page"]
            else:
                d["page"].set_default_timeout(1001)
                to_screenshot = d["page"].locator(payload.selector)
            await to_screenshot.screenshot(path=dest)
            with open(dest, "rb") as fh:
                binary_data = fh.read()
            os.remove(dest)
        return binary_data

    def obj_to_img_bytes(self, evaluation: typing.Any) -> bytes:
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
