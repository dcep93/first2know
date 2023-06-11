import json

from . import twitter_wrapper
from . import firebase_wrapper
from . import manager
from . import screenshot
from . import twitter_auth


def main():
    twitter_auth.login_access_token()
    print("oneoff complete")


if __name__ == "__main__":
    main()
