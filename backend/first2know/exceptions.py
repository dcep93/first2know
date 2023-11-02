import enum
import typing


class IgnorableException(Exception):
    pass


@enum.unique
class Src(enum.Enum):
    screenshot_null_location = "screenshot_null_location"
    playwright_screenshot = "playwright_screenshot"


def get_ignorable_exception(
        e: Exception,
        src: typing.Optional[Src] = None
) -> typing.Optional[IgnorableException]:
    if src == Src.playwright_screenshot:
        if str(e.__class__
               ) == "<class 'playwright._impl._api_types.TimeoutError'>":
            return IgnorableException("timeout")

    if src == Src.screenshot_null_location:
        if str(e.__class__) == "<class 'playwright._impl._api_types.Error'>":
            if e.getMessage() == "location: expected object, got null":
                return IgnorableException(f"1.{src.value}")

    return None
