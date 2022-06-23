import typing

from . import secrets
from . import firebase_wrapper
from . import recorded_sha
from . import screenshot
from . import twitter_wrapper


class Vars:
    _refresh_token: str
    _screenshot: typing.Any


def main():
    secrets.load_local()
    init()
    run_cron()


def init():
    print("refreshing access token")
    firebase_wrapper.init()
    old_refresh_token = firebase_wrapper.get_refresh_token()
    Vars._refresh_token = twitter_wrapper.refresh_access_token(
        old_refresh_token, )
    firebase_wrapper.write_refresh_token(Vars._refresh_token)
    Vars._screenshot = screenshot.SyncScreenshot()


def run_cron() -> bool:
    print(f"run_cron {recorded_sha.recorded_sha}")

    # if another process has spun up to take over, exit early
    new_refresh_token = firebase_wrapper.get_refresh_token()
    if new_refresh_token != Vars._refresh_token:
        return False

    to_handle = firebase_wrapper.get_to_handle()

    print(f"running {len(to_handle)}")
    [i for i in map(handle, to_handle)]

    print("done")
    return True


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    print(to_handle.key)
    cookie = None if to_handle.e_cookie is None else firebase_wrapper.decrypt(
        to_handle.e_cookie)
    payload = screenshot.RequestPayload(
        key=to_handle.key,
        url=to_handle.url,
        cookie=cookie,
        params=to_handle.params,
        evaluate=to_handle.evaluate,
        selector=to_handle.selector,
    )
    screenshot_response = Vars._screenshot.screenshot(payload)

    if screenshot_response is None:
        return

    current_data = screenshot_response.data
    if to_handle.data == current_data:
        return

    twitter_wrapper.tweet(to_handle.user, current_data)
    firebase_wrapper.write_data(to_handle.key, current_data)


if __name__ == "__main__":
    main()
