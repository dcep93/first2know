import concurrent.futures

from . import secrets
from . import firebase_wrapper
from . import recorded_sha
from . import screenshot
from . import twitter_wrapper

CONCURRENT_THREADS = 8


def main():
    secrets.load_local()
    run_cron()


def run_cron() -> None:
    print(f"run_cron {recorded_sha.recorded_sha}")

    firebase_wrapper.init()
    refresh_token = firebase_wrapper.get_refresh_token()
    new_refresh_token = twitter_wrapper.refresh_access_token(refresh_token)
    firebase_wrapper.write_refresh_token(new_refresh_token)

    to_handle = firebase_wrapper.get_to_handle()
    if secrets.Vars.is_remote:
        with concurrent.futures.ThreadPoolExecutor(
                CONCURRENT_THREADS, ) as executor:
            handled = executor.map(handle, to_handle)
    else:
        handled = [handle(i) for i in to_handle]  # noqa: F841

    print("done")


def handle(to_handle: firebase_wrapper.ToHandle) -> None:
    print(to_handle.key)
    cookie = None if to_handle.e_cookie is None else firebase_wrapper.decrypt(
        to_handle.e_cookie)
    payload = screenshot.RequestPayload(
        url=to_handle.url,
        cookie=cookie,
        params=to_handle.params,
        evaluate=to_handle.evaluate,
        selector=to_handle.selector,
    )
    screenshot_response = screenshot.screenshot(payload)

    if screenshot_response is None:
        return

    current_data = screenshot_response.data
    if to_handle.data == current_data:
        return

    twitter_wrapper.tweet(to_handle.user, current_data)
    firebase_wrapper.write_data(to_handle.key, current_data)


if __name__ == "__main__":
    main()
