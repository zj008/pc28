import requests
from requests.exceptions import ReadTimeout


def get(url, t=1):
    if t > 3:
        return ""
    try:
        ret = requests.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"},
            verify=False,
            timeout=10,
        )
    except ReadTimeout:
        return get(url, t+1)
    return ret.text