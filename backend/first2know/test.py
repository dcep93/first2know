import concurrent.futures
import time
import unittest

from . import crypt
from . import firebase_wrapper
from . import logger
from . import manager
from . import screenshot
from . import secrets

logger.logger.disabled = True


class TestFirst2Know(unittest.TestCase):
    def test_screenshot(self) -> None:
        data_input = firebase_wrapper.DataInput(url="https://example.com")
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
                evaluation=None,
            )
        )
        self.assertEqual(
            screenshot_response.md5,
            "72e9afeb37cd66e579ba16edac80f493",
        )

    def test_manager(self) -> None:
        data_input = firebase_wrapper.DataInput(url="https://example.com")
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

    def test_selector(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://example.com",
            selector="h1 >> nth=0",
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
                evaluation=None,
            )
        )
        self.assertEqual(
            screenshot_response.md5,
            "bbc1c4e4570a955433f2cecbc33d994f",
        )

    def test_evaluate(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://example.com",
            evaluate="document.body.innerHTML.substring(0, 20)",
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
                evaluation=None,
            )
        )
        self.assertEqual(
            "\n<div>\n    <h1>Examp",
            screenshot_response.evaluation,
        )

    def test_evaluation_to_img(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://example.com",
            evaluate="document.body.innerHTML",
            evaluation_to_img=True,
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
                evaluation=None,
            )
        )
        self.assertEqual(
            screenshot_response.md5,
            "80636eee396ece73b5ef8183b675013e",
        )

    def test_chain_evaluation(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://example.com",
            evaluate="(prev) => JSON.parse(prev) + 1",
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
                evaluation="420",
            )
        )
        self.assertEqual(
            screenshot_response.evaluation,
            "421",
        )

    def test_user_agent_hack(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://streeteasy.com/",
            evaluate="document.body.innerText",
            user_agent_hack=True,
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
            )
        )
        # SKIP
        # self.assertNotIn(
        #     "Press & Hold to confirm you are\na human (and not a bot).",
        #     screenshot_response.evaluation,
        # )

    def test_street_easy_requires_user_agent_hack(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://streeteasy.com/",
            evaluate="document.body.innerText",
        )
        screenshot_response = screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
            )
        )
        assert screenshot_response.evaluation is not None
        self.assertIn(
            "Press & Hold to confirm you are\na human (and not a bot).",
            screenshot_response.evaluation,
        )

        # def test_raw_proxy(self):
        #     data_input = firebase_wrapper.DataInput(
        #         url="https://streeteasy.com/building/170-amsterdam/05o",
        #         raw_proxy=True,
        #         params={"find": ["link[rel='stylesheet']", ".main-info"]},
        #         user_agent_hack=True,
        #         evaluate='document.head.innerHTML + document.body.innerHTML',
        #     )
        #     screenshot_response = screenshot.Screenshot()(screenshot.Request(
        #         data_input=data_input,
        #     ))
        #     starting_text = '<link href="//cdn-assets-s3.streeteasy.com/assets/'
        #     self.assertEqual(
        #         screenshot_response.evaluation[:len(starting_text)],
        #         starting_text,
        #     )
        #     self.assertEqual(
        #         screenshot_response.md5,
        #         '81e7d2419ef16e535e3112b0090f7d3e',
        #     )

    def test_ignore_short_circuit(self) -> None:
        data_input = firebase_wrapper.DataInput(
            url="https://example.com/",
            evaluate='"first2know_ignore"',
            selector=".invalid_selector",
        )
        screenshot.Screenshot()(
            screenshot.Request(
                data_input=data_input,
            )
        )

    def test_encryption_key_not_none(self) -> None:
        self.assertIsNotNone(secrets.Vars.secrets.email_password)

    def test_encryption(self) -> None:
        encrypyted = crypt.encrypt("hello world", "")
        self.assertIsNotNone(encrypyted)

    def test_decryption(self) -> None:
        # encrypted = crypt.encrypt("hello world", "")
        encrypted = "Z0FBQUFBQm93MUJ5a0laTHpJd3VSZU5EZlduWDE3NlQ0S010RDFMblVmLU5lY0JCMDExa2h4WDV6UFpmRE93Q2p3aUJpNG84SmZPOXFqYWt2clIzb2lqWFBnMzN1VFlLVnc9PQ=="
        decrypted = crypt.decrypt(encrypted, "")
        self.assertEqual(decrypted, "hello world")

    def test_encryption_uses_arg(self) -> None:
        a = crypt.encrypt("hello world", "")
        b = crypt.encrypt("hello world", "")
        self.assertEqual(a, b)
        c = crypt.encrypt("hello world", "c")
        self.assertNotEqual(a, c)

    def test_encrypt_decrypt(self) -> None:
        encrypted = "gAAAAABow1HzRLQP8va8Vx6SKky1-yFlVqdLOI-OXPWIqlBcTCfF8mkqLWbsGqoq1xulQ_Xm50DuSPFbMKqklLF3CeuBkTJzbb5uWte8OaNoYK52HiFW5b1_ibVGweId1wWSyQV0UO6E8dX2w8ipKoJ35Puq-svrvzbgTaCaiZu2CJzspdaCi3s="
        decrypted = crypt.decrypt(encrypted, "dcep93@gmail.com")
        print(decrypted)
