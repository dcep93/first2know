import typing

import modal

def get_modal_stub():
    image =  modal.DebianSlim()
    image.run_commands([
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "apt-get update",
        "pip install playwright==1.20.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    ])
    modal_app = modal.Stub(image=image)
    return modal_app

async def screenshot(
    url: str,
    css_selector: typing.Optional[str],
    fetch_params: typing.Dict[str, str],
) -> bytes:
    # TODO dcep93
    return bytes(url, 'utf-8')
    # from playwright.async_api import async_playwright # type: ignore

    # async with async_playwright() as p:
    #     print("Fetching url", url)
    #     browser = await p.chromium.launch()
    #     page = await browser.new_page()
    #     await page.goto(url)
    #     await page.screenshot(path="screenshot.png")
    #     await browser.close()
    #     data = open("screenshot.png", "rb").read()
    #     print("Screenshot of size %d bytes" % len(data))
    #     return data
