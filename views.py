
from django.http import HttpResponse
from django.shortcuts import render
import requests
from fake_useragent import UserAgent

from .models import Question, People

BASE_URL = "http://www.zhihu.com/"
request_headers = {"User-Agent": UserAgent().random,
                   "Referer": "http://www.zhihu.com/",
                   "Content-Type": "text/html; charset=utf-8"}


def index(request):
    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.order_by("name"),
        "people_following": People.objects.order_by("name"),
    })


def search(request):
    url = BASE_URL + "search"
    req = requests.get(url, params=request.GET, headers=request_headers)
    req.encoding = "utf-8"

    if req.status_code != requests.codes.ok:
        print(req.url)
        return HttpResponse(req.text, status=404)

    return HttpResponse(req.text)


def question(request, question_id):
    url = BASE_URL + "question/" + question_id
    req = requests.get(url, headers=request_headers)
    req.encoding = "utf-8"

    if req.status_code != requests.codes.ok:
        print(req.url, req.encoding)
        return HttpResponse(req.text, status=404)

    return HttpResponse(req.text)


def answer(request, question_id, answer_id):
    url = BASE_URL + "question/" + question_id + "/answer/" + answer_id
    req = requests.get(url, headers=request_headers)
    req.encoding = "utf-8"

    if req.status_code != requests.codes.ok:
        print(req.url)
        return HttpResponse(req.text, status=404)

    return HttpResponse(req.text)


def people(request, handle):
    url = BASE_URL + "people/" + handle
    req = requests.get(url, headers=request_headers)
    req.encoding = "utf-8"

    if req.status_code != requests.codes.ok:
        print(req.url)
        return HttpResponse(req.text, status=404)

    return HttpResponse(req.text)
