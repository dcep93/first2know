import requests
import json

access_token = "dmJtU09BcUtqYjQ1WVktc3Z6V3ZDVHJGdVVkTjdnczgyNG5Qd2FUREtwWWtpOjE2NTU4MzUwNTE5OTM6MTowOnJ0OjE"
data = "iVBORw0KGgoAAAANSUhEUgAABPAAAAAPCAYAAABqSDHcAAAAAXNSR0IArs4c6QAAA1ZJREFUeJzt3U0otF0cx/HfDFNzlYZGaiQbRTZeFlgoGzHewkQWXpZmJWWhxkaKWChFhPIyJbZSsxylFDJTXqKmQcnEToksJso8i6eucuN57sWtW9P3U9fmf871v85/++9c51gSiURCAAAAAAAAAH4k699eAAAAAAAAAICv0cADAAAAAAAAfjCrJA0NDamgoECGYSgvL0+Tk5OfTo5Go7Lb7fJ4PGbs6elJbrdbLpdLhmGopKREm5ub5ngoFJLb7VZmZqYyMjLU0NCgSCTyzWUBAAAAAAAAycEqSY+Pj1paWtLNzY3m5+c1Ojoqv9//buLb25u8Xq9KS0vfxW02mwYHBxUOh3V3d6fx8XF1dXWZTbpYLCaPx6ODgwOdnZ3J4XCosbFRHL0HAAAAAAAA/D/LZ5dYNDU1yeVyaWVlxYzNzMzo4uJCFotFt7e32tra+jTh+fm5ysrKtLGxofb29g/j4XBYFRUVisViys3N/YOlAAAAAAAAAMnnwxl4Ly8vOj09VXl5uRm7vr7W7OysJiYmvkzU1tYmp9OpoqIiFRYWqra29tN5oVBIOTk5ys7O/gPLBwAAAAAAAJJb6q+B/v5+5efnq7e314x5vV6NjY0pPT39y0TLy8t6eHhQIBCQJDkcjg9zIpGIRkZGtL6+rtTUD58GAAAAAAAA8It3XTSfz6ejoyNtb2+bDbbV1VVZrVZ1dnb+ZyKn0ymn06mBgQFVVlYqKytL3d3d5vjV1ZXq6uo0PT2t+vr6bygFAAAAAAAASD5mA8/n82lnZ0fBYPDdTrv9/X0Fg0FZLJZ3L6alpen5+fnTpCkpKTo5OTEbeJeXl6qpqdH4+Lh6enq+ow4AAAAAAAAgKVklaXBwUMFgUIFAQHa7XfF4XK+vr5L+/TU2kUiYT19fn1pbW83m3e7urtbW1hSLxXR/f6+FhQXt7e2pqqpKkhSNRlVdXa3h4WF1dHQoHo8rHo9zCy0AAAAAAADwG6zxeFxTU1M6Pj6Wy+WSYRgyDEPNzc2/lcBms2lxcVHFxcXKzc3V3NycFhYW1NLSIkny+/26vb2V1+s1cxuGocPDw++sCwAAAAAAAEgKlgRb4QAAAAAAAIAfy/q3FwAAAAAAAADgazTwAAAAAAAAgB/sH9yFAPbuL2cGAAAAAElFTkSuQmCC"

message_obj = {
    "command": "INIT",
    "total_bytes": 924,
    "media_type": "image/jpeg",
    "media_category": "tweet_image",
}
access_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
resp = requests.post(
    'https://upload.twitter.com/1.1/media/upload.json?',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}",
    },
    data=json.dumps(message_obj),
)
if resp.status_code >= 300:
    print(resp)
    print('x')
    print(resp.text)
    print('x')
    raise Exception(resp.text)
r = json.loads(resp.text)
print(r)
