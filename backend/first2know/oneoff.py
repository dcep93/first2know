import json

import pydantic  # type: ignore

from . import cron
from . import fetch_wrapped
from . import firebase_wrapper
from . import manager
from . import screenshot


def main() -> None:
    test_fetch_wrapped()
    print("oneoff complete")


def test_fetch_wrapped() -> None:
    results = fetch_wrapped.fetch_wrapped()
    print(json.dumps(results))


def handle_from_x() -> None:
    data = json.loads(
        """
    {
      "data_input": {
        "evaluate": "new Promise((resolve, reject) => {\\nfunction helper(i) {\\n  if (i < 0) return resolve(\\"first2know_ignore\\")\\n  const contents = Array.from(document.getElementsByClassName(\\"recentActivityDetail\\"))\\n    .map(e => e.innerText.split(\\"\\\\n\\"))\\n  if (contents.length > 0) {\\n    return resolve(JSON.stringify(contents, null, 2))\\n  }\\n  setTimeout(() => helper(i - 10), 10)\\n}\\nhelper(300)\\n})",
        "evaluation_to_img": false,
        "url": "https://example.com",
        "urlx": "https://fantasy.espn.com/football/recentactivity?leagueId=203836968"
      },
      "data_output": {
        "screenshot_data": {
          "md5": "",
          "evaluation": null
        },
        "time": 1686424278.642834
      },
      "user": {
        "email": "dcep93@gmail.com"
      }
    }
    """
    )
    data["key"] = ""
    to_handle = firebase_wrapper.ToHandle(**data)
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        1,
    )
    result = cron.handle(to_handle, screenshot_manager)
    print(result)


def screenshot_from_request() -> screenshot.Response:
    url = "https://fantasy.espn.com/football/recentactivity?leagueId=203836968"
    request = screenshot.Request(
        evaluation=None,
        data_input=firebase_wrapper.DataInput(
            url=url,
            evaluate='new Promise((resolve, reject) => {\nfunction helper(i) {\n  if (i < 0) return resolve(document.body.innerHTML || "first2know_ignore")\n  const contents = Array.from(document.getElementsByClassName("recentActivityDetail"))\n    .map(e => e.innerText.split("\\n"))\n  if (contents.length > 0) {\n    return resolve(JSON.stringify(contents, null, 2))\n  }\n  setTimeout(() => helper(i - 1), 10)\n}\nhelper(1000)\n})',
        ),
    )
    screenshot_response = screenshot.Screenshot()(request)
    return screenshot_response


if __name__ == "__main__":
    main()
