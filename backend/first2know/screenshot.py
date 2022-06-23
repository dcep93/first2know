import asyncio
import base64
import collections
import datetime
import json
import time
import typing

from pydantic import BaseModel


class RequestPayload(BaseModel):
    key: typing.Optional[str] = None
    url: str
    cookie: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, str]] = None
    evaluate: typing.Optional[str] = None
    selector: typing.Optional[str] = None


class ResponsePayload(BaseModel):
    data: str
    evaluate: typing.Optional[str]


# https://playwright.dev/python/docs/intro
class _Screenshot:
    def get_context(self, key: typing.Optional[str]):
        raise Exception("should be overridden")

    def execute_chain(
        self,
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ):
        raise Exception("should be overridden")

    def get_chain(
        self,
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ):
        return [
            ("context", lambda rval: self.get_context(payload.key)),
            ("page", lambda rval: rval["context"].new_page()),
            ("set_extra_http_headers",
             lambda rval: rval["page"].set_extra_http_headers(params)),
            ("goto", lambda rval: rval["page"].goto(payload.url)),
            # TODO dcep93 evaluate based on previous evaluation
            ("evaluate", lambda rval: None if payload.evaluate is None else
             rval["page"].evaluate(payload.evaluate)),
            ("locator",
             lambda rval: self.empty_apply(rval, {"locator": rval["page"]})
             if payload.selector is None else rval["page"].locator(payload.
                                                                   selector)),
            ("screenshot",
             lambda rval: rval["locator"].screenshot(path="screenshot.png")),
        ]

    def empty_apply(self, rval, to_apply):
        for i, j in to_apply.items():
            rval[i] = j
        return None

    # TODO dcep93 make robust
    def screenshot(self, payload: RequestPayload) -> ResponsePayload:
        s = time.time()

        params = {} if payload.params is None else dict(payload.params)
        if payload.cookie is not None:
            params["cookie"] = payload.cookie

        rval = self.execute_chain(params, payload)

        evaluate = json.dumps(rval.get("evaluate"))
        binary_data = open("screenshot.png", "rb").read()
        data = base64.b64encode(binary_data).decode('utf-8')
        print(' '.join([
            f"{time.time() - s:.3f}s",
            payload.key,
            f"{len(binary_data)/1000}kb",
            datetime.datetime.now().strftime("%H:%M:%S.%f"),
        ]))
        return ResponsePayload(data=data, evaluate=evaluate)


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
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ) -> typing.Dict[str, typing.Any]:
        chain = self.get_chain(params, payload)

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
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ) -> typing.Dict[str, typing.Any]:

        chain = self.get_chain(params, payload)
        rval = {}
        for i, c in chain:
            j = c(rval)
            if j is not None:
                rval[i] = j
        return rval
