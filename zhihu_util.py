
import requests
# from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re
import json

try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    PARSER = 'html.parser'

BASE_URL = "http://www.zhihu.com"
# chrome User-Agent
CHROME = "Mozilla/5.0 AppleWebKit/537.36 Chrome/52.0 Safari/537.36"
request_headers = {"User-Agent": CHROME,  # UserAgent().chrome,
                   "Referer": "http://www.zhihu.com/",
                   "Content-Type": "text/html; charset=utf-8"}
QUESTION_ID = re.compile(r"\d{6,10}")
PEOPLE_HANDLE = re.compile(r"[a-zA-Z0-9_-]{3,30}")


def grab_page(relative_url, follow_type, get_params=None):
    resp = requests.get(BASE_URL + relative_url, params=get_params,
                        headers=request_headers)
    resp.encoding = "utf-8"

    # print("got", relative_url, resp.status_code)
    # 404
    if resp.status_code != requests.codes.ok:
        return resp.status_code, resp.text

    return resp.status_code, \
        process_page(resp.text, relative_url, follow_type)


def insert_js(soup, elem, follow_type):
    print(elem.string)

    if follow_type == "answer":
        elem.string = "关注回答"

    script = soup.new_tag("script")
    script["type"] = "text/javascript"
    script["src"] = "/static/client/follow.js"
    elem.insert_after(script)

    # see follow.js
    elem["onclick"] = "follow({})".format(repr(follow_type))


def process_page(html, relative_url, follow_type):
    soup = BeautifulSoup(html, PARSER)
    # remove script
    for s in soup("script"):
        s.extract()

    # remove signin sidebar
    signin = soup.find("div", id="SidebarSignFlow")
    if signin is not None:
        signin.extract()
    # remove download app sidebar
    download = soup.find("div", class_="DownloadApp")
    if download is not None:
        download.extract()
    # remove footer
    footer = soup.find("div", id="zh-footer")
    if footer is not None:
        footer.extract()

    # no referrer for all img and css
    meta = soup.new_tag("meta")
    meta["name"] = "referrer"
    meta["content"] = "no-referrer"
    soup.head.append(meta)
    # image tag : no referrer
    # imgs = soup.find_all("img")
    # for img in imgs:
    #     img["referrerpolicy"] = "no-referrer"
    # provide css tag
    css_z = soup.new_tag("link")
    css_z["href"] = "/static/client/z_style.css"
    css_z["rel"] = "stylesheet"
    soup.head.append(css_z)
    css_main = soup.new_tag("link")
    css_main["href"] = "/static/client/main_style.css"
    css_main["rel"] = "stylesheet"
    soup.head.append(css_main)

    # calculate payload inside js
    if follow_type == "question":
        # follow question
        q_div = soup.select("#zh-question-side-header-wrap .follow-button")
        if q_div:
            insert_js(soup, q_div[0], "question")
    elif follow_type == "answer":
        a_div = soup.select("#zh-question-side-header-wrap .follow-button")
        if a_div:
            insert_js(soup, a_div[0], "answer")
    elif follow_type == "people":
        # follow people
        p_div = soup.select(".zm-profile-header-op-btns .zg-btn-follow")
        if p_div:
            insert_js(soup, p_div[0], "people")

    return str(soup)
