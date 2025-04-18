import enum
import typing


class IgnorableException(Exception):
    pass


@enum.unique
class Src(enum.Enum):
    screenshot_null_location = "screenshot_null_location"
    playwright_screenshot = "playwright_screenshot"


def get_ignorable_exception(
    e: Exception, src: typing.Optional[Src] = None
) -> typing.Optional[IgnorableException]:
    # print(e)
    # print('\n'.join(dir(e)))
    if src == Src.playwright_screenshot:
        if str(e.__class__) == "<class 'asyncio.exceptions.TimeoutError'>":
            return IgnorableException("asyncio_timeout")
        if str(e.__class__) == "<class 'playwright._impl._api_types.TimeoutError'>":
            return IgnorableException("playwright_timeout")
        if str(e.__class__) == "<class 'playwright._impl._api_types.Error'>":
            if e.message.startswith("Browser closed.\n"):  # type: ignore
                return IgnorableException("browser_closed")
            if e.message.startswith("net::ERR_CONNECTION_RESET at"):  # type: ignore
                return IgnorableException("connection_reset")

    if src == Src.screenshot_null_location:
        if str(e.__class__) == "<class 'playwright._impl._api_types.Error'>":
            if e.getMessage() == "location: expected object, got null":  # type: ignore
                return IgnorableException(f"1.{src.value}")

    return None
