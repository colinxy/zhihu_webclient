
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json

try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    PARSER = 'html.parser'

BASE_URL = "http://www.zhihu.com"
request_headers = {"User-Agent": UserAgent().chrome,
                   "Referer": "http://www.zhihu.com/",
                   "Content-Type": "text/html; charset=utf-8"}

# use of {{}} to represent {} for escaping formatting
JS_FETCH = """\
function(){{}}

fetch('/follow',{{ method:'POST',body:{},
headers: {{Content-Type: "application/json"}} }})
.then(function(resp) {{ if (resp.status==200) alert("success"); }})"""


def process_page(html, relative_url):
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

    # image tag : no referer
    imgs = soup.find_all("img")
    for img in imgs:
        img["referrerpolicy"] = "no-referrer"

    # post json data from url
    fromurl = relative_url[1:].split('/') \
        if relative_url[-1] != '/' else relative_url[1:-1].split('/')
    fromurl_it = iter(fromurl)
    payload = json.dumps(dict(zip(fromurl_it, fromurl_it)))

    # follow question
    q_div = soup.find("div", id="zh-question-side-header-wrap")
    if q_div is not None:
        # TODO
        script = soup.new_tag("script")
        script["type"] = "text/javascript"
        script.string = JS_FETCH.format(payload)
        soup.insert_after

        q_div["onclick"] = # JS_FETCH.format(payload)

    # follow people
    p_div = soup.select(".zm-profile-header-op-btns .zg-btn-follow")
    if p_div:
        script = soup.new_tag("script")
        script["type"] = "text/javascript"

        p_div[0]["onclick"] = JS_FETCH.format(payload)

    return str(soup)


def grab_page(relative_url, get_params=None):
    req = requests.get(BASE_URL + relative_url, params=get_params,
                       headers=request_headers)
    req.encoding = "utf-8"

    # 404
    if req.status_code != requests.codes.ok:
        return req.status_code, req.text

    return req.status_code, process_page(req.text, relative_url)
