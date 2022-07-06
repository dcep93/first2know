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
        pass


def run_tests():
    unittest.main()
