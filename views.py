
from .zhihu_util import grab_page, check_follow_payload

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

    try:
        payload_type = check_follow_payload(payload)
    except AttributeError as ex:
        print(ex)
        return HttpResponse(content_type="application/json", status=400)

    # follow question
    if "question" == payload_type:
        Question.objects.create(question_id=payload["question"],
                                name=payload["name"])
    # follow person
    elif "people" == payload_type:
        People.objects.create(handle=payload["people"],
                              name=payload["name"])

    return HttpResponse(content_type="application/json")
