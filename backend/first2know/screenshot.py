import asyncio
import base64
import collections
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
        pass

    def get_chain(
        self,
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ):
        return [
            lambda rval: {
                "context": self.get_context(payload.key)
            },
            lambda rval: {
                "page": rval["context"].new_page()
            },
            lambda rval: {
                "set_extra_http_headers":
                rval["page"].set_extra_http_headers(params)
            },
            lambda rval: {
                "goto": rval["page"].goto(payload.url)
            },
            lambda rval: {} if payload.evaluate is None else {
                "evaluate": rval["page"].evaluate(payload.evaluate)
            },
            lambda rval: self.empty_apply(rval, {"locator": rval["page"]})
            if payload.selector is None else {
                "locator": rval["page"].locator(payload.selector)
            },
            lambda rval: {
                "screenshot": rval["locator"].screenshot(path="screenshot.png")
            },
        ]

    def empty_apply(self, rval, to_apply):
        for i, j in to_apply.items():
            rval[i] = j
        return {}

    def execute_chain(
        self, statements: typing.List[typing.Callable]
    ) -> typing.Dict[str, typing.Any]:
        return {}

    # TODO dcep93 allow for local
    # TODO dcep93 make robust
    def screenshot(self, payload: RequestPayload) -> ResponsePayload:
        print(
            "Fetching url",
            payload.url,
            payload.key,
        )

        s = time.time()

        params = {} if payload.params is None else dict(payload.params)
        if payload.cookie is not None:
            params["cookie"] = payload.cookie

        rval = self.execute_chain(self.get_chain(params, payload))

        evaluate = json.dumps(rval.get("evaluate"))
        binary_data = open("screenshot.png", "rb").read()
        data = base64.b64encode(binary_data).decode('utf-8')
        print(
            time.time() - s,
            f"Screenshot of size {len(binary_data)} bytes",
            f"from {payload.url}",
        )
        return ResponsePayload(data=data, evaluate=evaluate)


class AsyncScreenshot(_Screenshot):
    async def get_context(self, key: typing.Optional[str]):
        from playwright.async_api import async_playwright as p  # type: ignore

        entered = await p().__aenter__()
        browser = await entered.chromium.launch()
        return await browser.new_context()

    def execute_chain(
        self, statements: typing.List[typing.Callable]
    ) -> typing.Dict[str, typing.Any]:
        async def helper():
            rval = {}
            for s in statements:
                t = s(rval)
                for i, j in t.items():
                    s = time.time()
                    print(i)
                    rval[i] = await j
                    print(time.time() - s, i)
            return rval

        return asyncio.run(helper())

    def get_chain(
        self,
        params: typing.Dict[str, str],
        payload: RequestPayload,
    ):
        super_chain = super().get_chain(params, payload)
        return super_chain + [
            lambda rval: {
                "context": rval["context"].close()
            },
        ]


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
        self, statements: typing.List[typing.Callable]
    ) -> typing.Dict[str, typing.Any]:

        rval = {}
        for s in statements:
            t = s(rval)
            for i, j in t.items():
                rval[i] = j
        return rval
