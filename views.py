
from django.http import HttpResponse
import requests
from fake_useragent import UserAgent

BASE_URL = "http://www.zhihu.com/"
user_agent = {"User-Agent": UserAgent().random}


def index(request):
    return HttpResponse("<h1>Welcome to Zhihu Client</h1>")


def question(request, question_id):
    url = BASE_URL + "question/" + question_id
    req = requests.get(url, headers=user_agent)

    if req.status_code != requests.codes.ok:
        print(url)
        return HttpResponse("not found")

    return HttpResponse(req.text)


def answer(request, question_id, answer_id):
    url = BASE_URL + "question/" + question_id + "/answer/" + answer_id
    req = requests.get(url, headers=user_agent)

    if req.status_code != requests.codes.ok:
        print(url)
        return HttpResponse("not found")

    return HttpResponse(req.text)


def people(request, handle):
    url = BASE_URL + "people/" + handle
    req = requests.get(url, headers=user_agent)

    if req.status_code != requests.codes.ok:
        print(url)
        return HttpResponse("not found")

    return HttpResponse(req.text)
