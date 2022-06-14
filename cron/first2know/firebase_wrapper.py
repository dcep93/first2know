# TODO dcep93
 
async def get_to_handle():
    return [
        {"key": "a", "user": "dcep93", "url": "https://chess.com", "img_data": None, "fetch_params": {}, "css_selector": None},
        {"key": "b", "user": "dcep93", "url": "https://www.chess.com/member/dcep93", "img_data": None, "fetch_params": {}, "css_selector": None},
    ]

async def write(key: str, img_data: bytes):
    print(key)
