import json

from . import twitter_wrapper
from . import firebase_wrapper
from . import manager
from . import screenshot


def main():
    img_data = 'iVBORw0KGgoAAAANSUhEUgAAAHcAAABzAQAAAACK06AxAAAAPElEQVR4nGNgGAWjYBRQCNgKD6Dw+W4nQBhMEIrDASrBAqEU/qLyOVVgAlDzYPph/J+o5o+CUTAKBgAAAPx/CBp43LB8AAAAAElFTkSuQmCC'
    img_url = twitter_wrapper.tweet(
        "test @dcep93",
        img_data,
    )
    print(img_url)
    print("oneoff complete")


if __name__ == "__main__":
    main()
