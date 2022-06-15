# TODO dcep93
 
def get_to_handle():
    return [
        {"key": "a", "user": "dcep93", "url": "https://chess.com", "img_data": "", "fetch_params": {}, "css_selector": None},
        {"key": "b", "user": "dcep93", "url": "https://www.chess.com/member/dcep93", "img_data": "", "fetch_params": {}, "css_selector": None},
    ]

def write_img_data(key: str, img_data: bytes):
    print("write_img_data", key)

def write_refresh_token(refresh_token: str):
    print("write_refresh_token", refresh_token)
