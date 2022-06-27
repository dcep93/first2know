import asyncio
import base64
import collections
import json
import io
import os
import typing

import abc

from pydantic import BaseModel

from PIL import Image, ImageDraw


class RequestPayload(BaseModel):
    url: str
    params: typing.Optional[typing.Dict[str, typing.Any]]
    evaluate: typing.Optional[str]
    evaluation_to_img: bool
    selector: typing.Optional[str]
    previous_evaluation: typing.Optional[typing.Any]


class ResponsePayload(BaseModel):
    img_data: str
    evaluation: typing.Any


# https://playwright.dev/python/docs/intro
class _Screenshot(abc.ABC):
    @abc.abstractmethod
    def get_context(self, key: typing.Optional[str]):
        raise Exception("should be overridden")

    @abc.abstractmethod
    def execute_chain(
        self,
        chain: typing.List[typing.Tuple[str, typing.Any]],
    ):
        raise Exception("should be overridden")

    def get_chain(
        self,
        key: str,
        payload: RequestPayload,
    ):
        params = None if payload.params is None else dict(payload.params)
        return [
            (
                "context",
                lambda d: self.get_context(key),
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
                    payload.evaluate, payload.previous_evaluation),
            ),
            (
                "to_screenshot",
                lambda d: self.get_to_screenshot(d, key, payload),
            ),
            (
                "screenshot",
                lambda d: None if d["to_screenshot"] is None else d[
                    "to_screenshot"].screenshot(path=d["dest"]),
            ),
        ]

    def get_to_screenshot(
        self,
        d: typing.Dict[str, typing.Any],
        key: str,
        payload: RequestPayload,
    ):
        if payload.evaluation_to_img:
            return None
        else:
            d["dest"] = f"screenshot_{key}.png"
            selector = "body" if payload.selector is None else payload.selector
            return d["page"].locator(selector)

    def screenshot(self, key: str, payload: RequestPayload) -> ResponsePayload:
        # s = time.time()
        chain = self.get_chain(key, payload)
        d = self.execute_chain(chain)
        if payload.evaluation_to_img:
            binary_data = self.evaluation_to_img_bytes(d["evaluation"])
        else:
            dest = d["dest"]
            binary_data = open(dest, "rb").read()
            os.remove(dest)
        img_data = base64.b64encode(binary_data).decode('utf-8')
        # print(' '.join([
        #     f"{time.time() - s:.3f}s",
        #     str(key),
        #     f"{len(rval)/1000}kb",
        #     datetime.datetime.now().strftime("%H:%M:%S.%f"),
        # ]))
        return ResponsePayload(
            img_data=img_data,
            evaluation=d["evaluation"],
        )

    def evaluation_to_img_bytes(self, evaluation: typing.Any) -> bytes:
        text = evaluation if type(evaluation) is str else json.dumps(
            evaluation,
            indent=1,
        )
        width = 100
        height = 100
        img = Image.new('1', (width, height))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, fill=255)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()


# TODO akshat make faster
class AsyncScreenshot(_Screenshot):
    async def get_context(self, key: typing.Optional[str]):
        from playwright.async_api import async_playwright as p  # type: ignore

        self.p = p()

        entered = await self.p.__aenter__()
        self.browser = await entered.chromium.launch()
        self.context = await self.browser.new_context()
        return self.context

    async def close(self):
        await self.context.close()
        await self.browser.close()
        await self.p.__aexit__()

    def execute_chain(
        self,
        chain: typing.List[typing.Tuple[str, typing.Any]],
    ) -> typing.Dict[str, typing.Any]:
        async def helper():
            rval = {}
            for i, c in chain:
                j = c(rval)
                if j is not None:
                    rval[i] = await j
            await self.close()
            return rval

        return asyncio.run(helper())


class SyncScreenshot(_Screenshot):
    browser: typing.Any
    contexts: collections.defaultdict

    def __init__(self):
        super().__init__()
        from playwright.sync_api import sync_playwright as p  # type: ignore

        entered = p().__enter__()
        self.browser = entered.chromium.launch()
        self.contexts = collections.defaultdict(self._make_context)

    def _make_context(self):
        return self.browser.new_context()

    def get_context(self, key: str):
        return self.contexts[key]

    def execute_chain(
        self,
        chain: typing.List[typing.Tuple[str, typing.Any]],
    ) -> typing.Dict[str, typing.Any]:
        rval = {}
        for i, c in chain:
            j = c(rval)
            if j is not None:
                rval[i] = j
        return rval
