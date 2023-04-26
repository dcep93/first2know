import json

from . import firebase_wrapper
from . import manager
from . import screenshot


def main():
    url = "https://www.stubhub.com/taylor-swift-east-rutherford-tickets-5-26-2023/event/150593661/"
    request = screenshot.Request(data_input=firebase_wrapper.DataInput(
        url=url,
        raw_proxy=True,
        params={
            "method": "POST",
            "data": {
                "Quantity": 1,
            }
        },
        evaluate="document.body.innerHTML",
    ), )
    screenshot_response = screenshot.Screenshot()(request)
    print(json.dumps(screenshot_response.evaluation))
    print("oneoff complete")


if __name__ == "__main__":
    main()
