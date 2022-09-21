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

    def log(self, s: str):
        if secrets.Vars.is_local:
            print(self.id, s)

    def __call__(self, request: Request) -> Response:
        r = asyncio.run(self.__acall__(request))
        return r

    async def __acall__(
        self,
        request: Request,
    ) -> Response:

        s = time.time()

        class C:
            _c = 0

            @classmethod
            def c(cls):
                cls._c += 1
                print(cls._c, time.time() - s)

        C.c()

        params = dict(request.data_input.params)

        if request.data_input.user_agent_hack:
            params["user-agent"] = GOOD_USER_AGENT

        context = await self.browser.new_context()
        page = await context.new_page()
        C.c()

        if request.data_input.raw_proxy:
            proxy_result = proxy.proxy(
                proxy.Request(
                    url=request.data_input.url,
                    params=proxy.Params(**params),
                ))
            await page.set_content(proxy_result)
        elif request.data_input.url:
            await page.set_extra_http_headers(params)
            await page.goto(request.data_input.url)
        C.c()
        evaluation = None \
            if request.data_input.evaluate is None \
            else await page.evaluate(
                request.data_input.evaluate,
                request.evaluation,
            )
        C.c()
        if request.data_input.evaluation_to_img:
            text = evaluation \
                if type(evaluation) is str \
                else json.dumps(evaluation, indent=1)
            lines = text.split("\n")
            padding_pixels = 50
            pixels_per_row = 15.5
            pixels_per_column = 7
            width = 2 * padding_pixels + (pixels_per_column *
                                          max([len(i) for i in lines]))
            height = int(2 * padding_pixels + (pixels_per_row * len(lines)))
            img = Image.new('1', (width, height))
            draw = ImageDraw.Draw(img)
            draw.text((padding_pixels, padding_pixels), text, fill=255)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            binary_data = img_byte_arr.getvalue()
        else:
            dest = f"screenshot_{self.id}.png"
            if request.data_input.selector is None:
                to_screenshot = page
            else:
                page.set_default_timeout(1001)
                to_screenshot = page.locator(request.data_input.selector)
            await to_screenshot.screenshot(path=dest)
            with open(dest, "rb") as fh:
                binary_data = fh.read()
            os.remove(dest)
        C.c()

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
        C.c()
        return Response(
            img_data=img_data,
            evaluation=evaluation,
            md5=md5,
            elapsed=elapsed,
        )
