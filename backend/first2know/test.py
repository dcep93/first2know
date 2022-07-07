import unittest

from . import screenshot
from . import firebase_wrapper


class TestScreenshot(unittest.TestCase):
    def test_screenshot(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate=None,
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.AsyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        self.assertEqual(
            screenshot_response.md5,
            "c5ab4b20641f3de2ca9bdb0ed6a88f9a",
        )

    def test_selector(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector="h1 >> nth=0",
            evaluate=None,
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        self.assertEqual(
            screenshot_response.md5,
            "814ff58bd2a6352eb89e8deffbf03510",
        )

    def test_evaluate(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate="document.body.innerHTML.substring(0, 20)",
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        self.assertEqual(
            screenshot_response.evaluation,
            '\n<div>\n    <h1>Examp',
        )

    def test_evaluation_to_img(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate="document.body.innerHTML",
            evaluation_to_img=True,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        self.assertEqual(
            screenshot_response.md5,
            "ceb5b009d8f6cd71b72b0ec35a0f8896",
        )

    def test_chain_evaluation(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate="(prev) => prev + 1",
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            420,
        )
        self.assertEqual(
            screenshot_response.evaluation,
            421,
        )
