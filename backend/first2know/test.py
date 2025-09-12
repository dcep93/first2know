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

    def test_encryption_key_hash(self) -> None:
        hashed = crypt.str_to_md5(secrets.Vars.secrets.email_password)
        self.assertEqual(hashed, "493103cd268655109304a2e860830394")

    def test_encryption(self) -> None:
        encrypyted = crypt.encrypt("hello world", "")
        self.assertIsNotNone(encrypyted)

    def test_keygen(self) -> None:
        fernet_key_bytes = crypt.get_fernet_key_bytes("email@email.email")
        decoded = fernet_key_bytes.decode("utf-8")
        self.assertEqual(decoded, "NmVjNGEyNTFmN2IxZTBlZWQ1MTk1NzcyYmQzNThlOGE=")

    def test_decryption(self) -> None:
        encrypted = crypt.encrypt("hello world", "")
        decrypted = crypt.decrypt(encrypted, "")
        self.assertEqual(decrypted, "hello world")

    def test_specific_deecryption(self) -> None:
        encrypted = "gAAAAABow3Ulf6dl3pQ3bnD3byklasjcLGdRAmA99jDzJrD6vvXYvfxnOzjOFibVDvCSq3bEwjDnfEbDPuIlHKkJ-_Fh7ljnJw=="
        decrypted = crypt.decrypt(encrypted, "")
        self.assertEqual(decrypted, "hello world")

    def test_encryption_uses_arg(self) -> None:
        a = crypt.encrypt("hello world", "")
        b = crypt.encrypt("hello world", "")
        self.assertEqual(a, b)
        c = crypt.encrypt("hello world", "c")
        self.assertNotEqual(a, c)
