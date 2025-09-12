from pathlib import Path

from . import firebase_wrapper
from . import manager
from . import screenshot
from . import secrets

with open(Path(__file__).parent / "fetch_wrapped.js") as fh:
    contents = fh.read()


def fetch_wrapped(screenshot_manager: manager.Manager) -> str | None:
    screenshot_response = screenshot_manager.run(
        screenshot.Request(
            data_input=firebase_wrapper.DataInput(
                url="https://lm-api-reads.fantasy.espn.com",
                cookies={
                    "https://lm-api-reads.fantasy.espn.com": {
                        "espn_s2": secrets.Vars.secrets.espn_s2
                    }
                },
                evaluate=contents,
            ),
        )
    )
    return screenshot_response.evaluation
