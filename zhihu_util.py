
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
# chrome User-Agent
# Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36
# (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36
request_headers = {"User-Agent": UserAgent().chrome,
                   "Referer": "http://www.zhihu.com/",
                   "Content-Type": "text/html; charset=utf-8"}

# use of {{}} to represent {} for escaping formatting
JS_FETCH = """\
function getCookie(name) {{
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {{
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {{
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                cookieValue =
                    decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }}
        }}
    }}
    return cookieValue;
}}
function follow(){{
    fetch('/follow',{{
        method:'POST',
        credentials:'same-origin',
        body:'{}',
        headers:{{"Content-Type":"application/json",
                  "Origin":document.origin,
                  "X-CSRFToken":getCookie("csrftoken"),}}
    }})
    .then(function(resp) {{ if (resp.status==200) alert("success"); }});
}}"""
# to pass django csrf check, both credentials(cookie) and X-CSRFToken needed


def insert_js(soup, elem, payload):
    script = soup.new_tag("script")
    script["type"] = "text/javascript"
    script.string = JS_FETCH.format(payload)
    elem.insert_after(script)
    elem["onclick"] = "follow()"


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

    meta = soup.new_tag("meta")
    meta["name"] = "referrer"
    meta["content"] = "no-referrer"
    soup.head.append(meta)
    # image tag : no referrer
    # imgs = soup.find_all("img")
    # for img in imgs:
    #     img["referrerpolicy"] = "no-referrer"
    # css tag : no referrer

    # post json data from url
    fromurl = relative_url[1:].split('/') \
        if relative_url[-1] != '/' else relative_url[1:-1].split('/')
    fromurl_it = iter(fromurl)
    payload = json.dumps(dict(zip(fromurl_it, fromurl_it)))
    print(payload)

    # follow question
    q_div = soup.find("div", id="zh-question-side-header-wrap")
    if q_div is not None:
        insert_js(soup, q_div, payload)
    else:
        # follow people
        p_div = soup.select(".zm-profile-header-op-btns .zg-btn-follow")
        if p_div:
            insert_js(soup, p_div[0], payload)

    return str(soup)


def grab_page(relative_url, get_params=None):
    resp = requests.get(BASE_URL + relative_url, params=get_params,
                        headers=request_headers)
    resp.encoding = "utf-8"

    # print("got", relative_url, resp.status_code)
    # 404
    if resp.status_code != requests.codes.ok:
        return resp.status_code, resp.text

    return resp.status_code, process_page(resp.text, relative_url)
