import asyncio
import base64
import collections
import json
import os
import typing

import abc

from pydantic import BaseModel


class RequestPayload(BaseModel):
    url: str
    params: typing.Optional[typing.Dict[str, str]]
    evaluate: typing.Optional[str]
    selector: typing.Optional[str]
    previous_evaluation: typing.Optional[str]


class ResponsePayload(BaseModel):
    img_data: str
    evaluated: typing.Optional[str]


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
        screenshot_dest: str,
    ):
        params = None if payload.params is None else dict(payload.params)
        return [
            (
                "context",
                lambda rval: self.get_context(key),
            ),
            (
                "page",
                lambda rval: rval["context"].new_page(),
            ),
            (
                "set_extra_http_headers",
                lambda rval: rval["page"].set_extra_http_headers(params),
            ),
            (
                "goto",
                lambda rval: rval["page"].goto(payload.url),
            ),
            # TODO dcep93 evaluate based on previous evaluation
            (
                "evaluate",
                lambda rval: None
                if payload.evaluate is None else rval["page"].evaluate(
                    payload.evaluate, payload.previous_evaluation),
            ),
            (
                "selector",
                lambda rval: self.empty_apply(rval, {"selector": rval["page"]})
                if payload.selector is None else rval["page"].locator(
                    payload.selector),
            ),
            (
                "screenshot",
                lambda rval: rval["selector"].screenshot(path=screenshot_dest),
            ),
            # TODO dcep93 text to img
        ]

    def empty_apply(self, rval, to_apply):
        for i, j in to_apply.items():
            rval[i] = j
        return None

    # TODO dcep93 make robust
    def screenshot(self, key: str, payload: RequestPayload) -> ResponsePayload:
        # s = time.time()
        dest = f"screenshot_{key}.png"

        chain = self.get_chain(key, payload, dest)
        rval = self.execute_chain(chain)
        evaluated = json.dumps(rval.get("evaluate"))
        binary_data = open(dest, "rb").read()
        os.remove(dest)
        img_data = base64.b64encode(binary_data).decode('utf-8')
        # print(' '.join([
        #     f"{time.time() - s:.3f}s",
        #     str(payload.key),
        #     f"{len(binary_data)/1000}kb",
        #     datetime.datetime.now().strftime("%H:%M:%S.%f"),
        # ]))
        return ResponsePayload(img_data=img_data, evaluated=evaluated)


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
