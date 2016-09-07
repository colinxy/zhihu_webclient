
from .zhihu_util import grab_page

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
import requests
import json

from .models import Question, People


def index(request):
    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.order_by("name"),
        "people_following": People.objects.order_by("name"),
    })


def search(request):
    status_code, html_str = grab_page("/search", request.GET)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


def topic(request, topic_id):
    status_code, html_str = grab_page("/topic/" + topic_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


@ensure_csrf_cookie
def question(request, question_id):
    status_code, html_str = grab_page("/question/" + question_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


@ensure_csrf_cookie
def answer(request, question_id, answer_id):
    status_code, html_str = grab_page("/question/" + question_id +
                                      "/answer/" + answer_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


@ensure_csrf_cookie
def people(request, handle):
    status_code, html_str = grab_page("/people/" + handle)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


def follow_confirm(request):
    payload = json.loads(request.body.decode("utf-8"))
    print(payload)

    # follow question
    if "question" in payload:
        print(Question.objects.all())

    # follow person
    if "people" in payload:
        print(People.objects.all())

    return HttpResponse(content_type="application/json")
