from . import screenshot
from . import firebase_wrapper

import unittest


class TestScreenshot(unittest.TestCase):
    def test_sync_screenshot(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate=None,
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        h = hash(screenshot_response.img_data)
        assert h == 0
        assert screenshot_response.evaluation is None

    def test_async_screenshot(self):
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
        h = hash(screenshot_response.img_data)
        assert h == 0
        assert screenshot_response.evaluation is None

    def test_evaluate(self):
        data_input = firebase_wrapper.DataInput(
            url="https://example.org",
            params={},
            selector=None,
            evaluate="document.body.innerHTML",
            evaluation_to_img=False,
        )
        screenshot_response = screenshot.SyncScreenshot().screenshot(
            "",
            data_input,
            None,
        )
        assert screenshot_response.evaluation is not None
        h = hash(screenshot_response.evaluation)
        assert h == 0

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
        h = hash(screenshot_response.img_data)
        assert h == 0

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
        assert screenshot_response.evaluation == 421


def run_tests():
    unittest.main()
