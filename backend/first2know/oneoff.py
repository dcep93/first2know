import json

import pydantic

from . import cron
from . import twitter_wrapper
from . import firebase_wrapper
from . import manager
from . import screenshot
from . import twitter_auth


def main():
    cron.loop(1)
    print("oneoff complete")


def handle_from_x():
    data = json.loads('''
    {
      "data_input": {
        "evaluate": "new Promise((resolve, reject) => {\\nfunction helper(i) {\\n  if (i < 0) return resolve(\\"first2know_ignore\\")\\n  const contents = Array.from(document.getElementsByClassName(\\"recentActivityDetail\\"))\\n    .map(e => e.innerText.split(\\"\\n\\"))\\n  if (contents.length > 0) {\\n    return resolve(JSON.stringify(contents, null, 2))\\n  }\\n  setTimeout(() => helper(i - 1), 10)\\n}\\nhelper(30000)\\n})",
        "evaluation_to_img": false,
        "url": "https://fantasy.espn.com/football/recentactivity?leagueId=203836968"
      },
      "data_output": {
        "screenshot_data": {
          "img_url": "https://pbs.twimg.com/media/FySHdEhWYAYnAZk.jpg",
          "md5": "c2cb5bd5ff26bff7d0ebd712111ed45c",
          "evaluation": null
        },
        "time": 1686424278.642834
      },
      "md5": "8de637f8392faa41114f3a335ed113e0",
      "user": {
        "encrypted": "Z0FBQUFBQmtoY1VlRDVMVXFQblRIZ0NnbVU5bHl2dVM3SFk4bFRrcDdOUWNhVjdKSGh0ZzNIclRURlZRRVhGd0UzTDhWeXA2THBWb05OTGpWN2NUVnp5SDFkZWk0cWlqQjNxaVNlek5YZmVIb1A2TEFLdHdXR3dTLVdPNXlTMm9NTlh1VTJ6T0RoaEMwOC11VWY2M0NuTlcwY3lqUllIOV9IZXlvM01SaE5UbFdYejBCOTlkMkdyWVdZallzdTZzMHFuX1NLbjV3UmJFZDBZYTduV24xWUFDVnZTX3JibWZOV0xzUUxPWTVKcl85ZTJkeUh6N1cybWlBeW91UndndTEyS1FFbjNJMDN1dmF4MnNYRUZFUmsxOFZOUjIyV3JkSGhZMUw5c01lUjhMdS02M0MwSExqbXR5WF8ta3k1YWQ3d3JpbTBIeDB2OUt3ZVBDRVliQjhuSTR1ZlhOT3h4YTMya09zU3k0MlZvY0V0R0F1VDF0aFQwd1J6VnNrWUtJczVudWg5S0hTMnBlYkZqaGxJM1pxUFdUYTFNQVFyWnNMRGlVUV9MUllreGlUcjVLQkJpQ3N4NVZBSDFyeDBaQ2ZsbTBDNlNYNHhpQjV3aUp3T1dXNjhXbXJTODdEOXMtZm5aMjVTYk01Q0xVVlBkOWpNMmFIOUtJUXVialhzeHJlM0hSQjExbVJqR3M=",
        "screen_name": "dcep93",
        "user_id": 3260667476
      }
    }
    ''')
    data["key"] = ""
    to_handle = firebase_wrapper.ToHandle(**data)
    screenshot_manager = manager.Manager(
        screenshot.Screenshot,
        1,
    )
    result = cron.handle(to_handle, screenshot_manager)
    print(result)


def screenshot_from_request():
    url = "https://fantasy.espn.com/football/recentactivity?leagueId=203836968"
    request = screenshot.Request(
        evaluation=None,
        data_input=firebase_wrapper.DataInput(
            url=url,
            evaluate=
            "new Promise((resolve, reject) => {\nfunction helper(i) {\n  if (i < 0) return resolve(document.body.innerHTML || \"first2know_ignore\")\n  const contents = Array.from(document.getElementsByClassName(\"recentActivityDetail\"))\n    .map(e => e.innerText.split(\"\\n\"))\n  if (contents.length > 0) {\n    return resolve(JSON.stringify(contents, null, 2))\n  }\n  setTimeout(() => helper(i - 1), 10)\n}\nhelper(1000)\n})",
        ),
    )
    screenshot_response = screenshot.Screenshot()(request)
    return screenshot_response


if __name__ == "__main__":
    main()
