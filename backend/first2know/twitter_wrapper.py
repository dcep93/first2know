import time

import twitter_auth

async def tweet(user: str, img_data: bytes):
    print(f"tweeting to {user} {len(img_data)}")
    access_token = "aXFPc0VjLXBtYUtiTS0xdXBtcHV4M1FscW9RQWJlbXFzd1BlbjMzdGNCXzJiOjE2NTUyNjAxNDc3OTE6MTowOmF0OjE"
    message_obj = {"text": f"@{user} {len(img_data)} {time.time()}"}
    twitter_auth.post_tweet(access_token, message_obj)
