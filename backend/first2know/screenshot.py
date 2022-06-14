async def screenshot(url):
    from playwright.async_api import async_playwright # type: ignore

    async with async_playwright() as p:
        print("Fetching url", url)
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path="screenshot.png")
        await browser.close()
        data = open("screenshot.png", "rb").read()
        print("Screenshot of size %d bytes" % len(data))
        return data