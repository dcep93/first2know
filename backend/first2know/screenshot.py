import asyncio
import base64
import datetime
import io
import json
import os
import time
import typing
import uuid

from pydantic import BaseModel  # type: ignore

from PIL import Image, ImageDraw  # type: ignore

from . import crypt
from . import exceptions
from . import firebase_wrapper
from . import logger
from . import manager
from . import proxy

import nest_asyncio  # type: ignore

C_LOG_SECONDS = 10
GOOD_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"  # noqa


T = typing.TypeVar("T")


class Register(BaseModel, typing.Generic[T]):
    value: T


Timer = Register[list[tuple[str, float]]]


class Request(BaseModel):
    key: str
    data_input: firebase_wrapper.DataInput
    evaluation: typing.Optional[str] = None
    timer: typing.Optional[Timer] = None


class Response(BaseModel):
    img_data: str
    evaluation: typing.Optional[str]
    md5: str
    elapsed: float
    timer: Timer


Manager = manager.Manager[Request, Response]


# https://playwright.dev/python/docs/intro
class Screenshot:

    def __init__(self) -> None:
        nest_asyncio.apply()
        self.id = str(uuid.uuid1())
        self.p, self.browser = asyncio.run(self.async_init())

    async def async_init(self) -> typing.Tuple[typing.Any, typing.Any]:
        from playwright.async_api import async_playwright as _p  # type: ignore # noqa

        p = _p()

        entered = await p.__aenter__()
        browser = await entered.chromium.launch()

        return p, browser

    async def close(self) -> None:
        await self.browser.close()
        await self.p.__aexit__()

    def log(self, s: str) -> None:
        logger.log(f"screenshot.log.log {self.id} {s}")

    def __call__(self, request: Request) -> Response:

        r = asyncio.run(self.__acall__(request))
        return r

    async def __acall__(
        self,
        request: Request,
    ) -> Response:
        timer = request.timer or Timer(value=[])
        s = time.time()

        latest = Register(value=s)

        def C(key: str) -> None:
            now = time.time()
            diff = now - latest.value
            latest.value = now
            timer.value.append((key, round(diff, 2)))
            if diff > C_LOG_SECONDS:
                logger.log(f"screenshot.C {key} {request.key} {diff}")

        C("init")

        params = dict(request.data_input.params or {})

        if request.data_input.user_agent_hack:
            params["user-agent"] = GOOD_USER_AGENT

        context = await self.browser.new_context()
        try:
            if request.data_input.cookies:
                await context.add_cookies(
                    [
                        {"name": k2, "value": v2, "domain": k1, "path": "/"}
                        for k1, v1 in request.data_input.cookies.items()
                        for k2, v2 in v1.items()
                    ]
                )
            page = await context.new_page()
            page.set_default_timeout(30001)
            C("new_page")
            try:
                if request.data_input.raw_proxy:
                    if not request.data_input.url:
                        raise Exception("raw_proxy.url.false")
                    proxy_result = proxy.proxy(
                        proxy.Request(
                            url=request.data_input.url,
                            params=proxy.Params(**params),
                        )
                    )
                    await page.set_content(proxy_result)
                elif request.data_input.url:
                    await page.set_extra_http_headers(params)
                    await page.goto(request.data_input.url)
            finally:
                C("goto")
            raw_evaluation = (
                None
                if request.data_input.evaluate is None
                else await page.evaluate(
                    request.data_input.evaluate,
                    request.evaluation,
                )
            )
            C("eval")
            str_evaluation = (
                raw_evaluation
                if type(raw_evaluation) is str
                else json.dumps(raw_evaluation)
            )

            if (
                request.data_input.evaluation_to_img
                or raw_evaluation == exceptions.IGNORE
            ):
                img_data = str_to_binary_data(str_evaluation)
            else:
                if request.data_input.selector is None:
                    to_screenshot = page
                else:
                    to_screenshot = page.locator(request.data_input.selector)
                dest = f"screenshot_{self.id}.png"

                try:
                    await to_screenshot.screenshot(path=dest, timeout=10001)
                except Exception as e:
                    ignorable_exception = exceptions.get_ignorable_exception(
                        e,
                        exceptions.Src.screenshot_null_location,
                    )
                    if not ignorable_exception is None:
                        raise ignorable_exception
                    raise e

                with open(dest, "rb") as fh:
                    binary_data = fh.read()
                os.remove(dest)
                encoded = base64.b64encode(binary_data)
                img_data = encoded.decode("utf-8")
        finally:
            await context.close()
        C("screenshot")

        if raw_evaluation is None:
            md5 = crypt.str_to_md5(img_data)
            evaluation = None
        else:
            evaluation = str_evaluation
            md5 = crypt.str_to_md5(str_evaluation)
        elapsed = time.time() - s
        self.log(
            " ".join(
                [
                    "screenshot.__acall__",
                    f"{elapsed:.3f}s",
                    f"{len(img_data)/1000}kb",
                    datetime.datetime.now().strftime("%H:%M:%S.%f"),
                ]
            )
        )
        C("finish")
        return Response(
            img_data=img_data,
            evaluation=evaluation,
            md5=md5,
            elapsed=elapsed,
            timer=timer,
        )


def str_to_binary_data(s: str) -> str:
    text = s.encode("latin-1", "ignore").decode("latin-1")
    lines = text.split("\n")
    padding_pixels = 50
    pixels_per_row = 15.2
    pixels_per_column = 6.6
    width = int(2 * padding_pixels + (pixels_per_column * max([len(i) for i in lines])))
    height = int(2 * padding_pixels + (pixels_per_row * len(lines)))
    img = Image.new("1", (width, height))
    draw = ImageDraw.Draw(img)
    draw.text((padding_pixels, padding_pixels), text, fill=255)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    binary_data = img_byte_arr.getvalue()
    encoded = base64.b64encode(binary_data)
    img_data = encoded.decode("utf-8")
    return img_data
