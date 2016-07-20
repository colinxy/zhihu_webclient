
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    PARSER = 'html.parser'

BASE_URL = "http://www.zhihu.com"
request_headers = {"User-Agent": UserAgent().chrome,
                   "Referer": "http://www.zhihu.com/",
                   "Content-Type": "text/html; charset=utf-8"}


def add_follow(html, relative_url):
    soup = BeautifulSoup(html, PARSER)
    # follow question
    div = soup.find("div", id="zh-question-side-header-wrap")
    if div is not None:
        div["onclick"] = "location.href='{}'".format("/follow" + relative_url)

    return str(soup)


def grab_page(relative_url, get_params=None):
    req = requests.get(BASE_URL + relative_url, params=get_params,
                       headers=request_headers)
    req.encoding = "utf-8"

    # 404
    if req.status_code != requests.codes.ok:
        return req.status_code, req.text

    return req.status_code, add_follow(req.text, relative_url)
