import concurrent.futures
import time
import unittest

from . import firebase_wrapper
from . import manager
from . import screenshot


class TestScreenshot(unittest.TestCase):
    def test_screenshot(self):
        data_input = firebase_wrapper.DataInput(url="https://example.org")
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input,
            evaluation=None,
        ))
        self.assertEqual(
            screenshot_response.md5,
            "c5ab4b20641f3de2ca9bdb0ed6a88f9a",
        )

    def test_manager(self):
        data_input = firebase_wrapper.DataInput(url="https://example.org")
        num_to_run = 2
        r = screenshot.Request(
            data_input=data_input,
            evaluation=None,
        )
        m = manager.Manager(screenshot.Screenshot, num_to_run)
        try:
            with concurrent.futures.ThreadPoolExecutor(num_to_run) as executor:
                s = time.time()
                _responses = executor.map(
                    m.run,
                    [r for _ in range(num_to_run)],
                )
                responses = list(_responses)
                e = time.time()
        finally:
            m.close()
        elapsed = e - s
        total = sum([i.elapsed for i in responses])
        self.assertLess(elapsed, total)

    def test_selector(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            selector="h1 >> nth=0",
        )
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input,
            evaluation=None,
        ))
        self.assertEqual(
            screenshot_response.md5,
            "814ff58bd2a6352eb89e8deffbf03510",
        )

    def test_evaluate(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            evaluate="document.body.innerHTML.substring(0, 20)",
        )
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input,
            evaluation=None,
        ))
        self.assertEqual(
            screenshot_response.evaluation,
            '\n<div>\n    <h1>Examp',
        )

    def test_evaluation_to_img(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            evaluate="document.body.innerHTML",
            evaluation_to_img=True,
        )
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input,
            evaluation=None,
        ))
        self.assertEqual(
            screenshot_response.md5,
            "ceb5b009d8f6cd71b72b0ec35a0f8896",
        )

    def test_chain_evaluation(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            evaluate="(prev) => prev + 1",
        )
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input,
            evaluation=420,
        ))
        self.assertEqual(
            screenshot_response.evaluation,
            421,
        )

    def test_user_agent_hack(self):
        data_input = firebase_wrapper.DataInput(
            url="https://streeteasy.com/",
            evaluate="document.body.innerHTML",
            user_agent_hack=True,
        )
        screenshot_response = screenshot.Screenshot()(screenshot.Request(
            data_input=data_input, ))
        self.assertEqual(
            screenshot_response.evaluation,
            421,
        )
