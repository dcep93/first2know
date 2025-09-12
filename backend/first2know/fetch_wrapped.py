from pathlib import Path

from . import firebase_wrapper
from . import manager
from . import screenshot
from . import secrets

with open(Path(__file__).parent / "fetchWrapped.js") as fh:
    contents = fh.read()

data_input = firebase_wrapper.DataInput.parse_obj(
    {
        "cookies": {"espn_s2": secrets.Vars.secrets.espn_s2},
        # "evaluate": contents,
    }
)


def fetch_wrapped(screenshot_manager: manager.Manager) -> None:
    screenshot_response = screenshot_manager.run(
        screenshot.Request(
            data_input=data_input,
        )
    )
