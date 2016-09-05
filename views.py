
from .zhihu_util import grab_page

from django.http import HttpResponse
from django.shortcuts import render
import requests

from .models import Question, People


def index(request):
    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.order_by("name"),
        "people_following": People.objects.order_by("name"),
    })


def search(request):
    status_code, html = grab_page("/search", request.GET)

    if status_code != requests.codes.ok:
        return HttpResponse(html, status=404)

    return HttpResponse(html)


def topic(request, topic_id):
    status_code, html = grab_page("/topic/" + topic_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html, status=404)

    return HttpResponse(html)


def question(request, question_id):
    status_code, html = grab_page("/question/" + question_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html, status=404)

    return HttpResponse(html)


def answer(request, question_id, answer_id):
    status_code, html = grab_page("/question/{}/answer/{}".
                                  format(question_id, answer_id))

    if status_code != requests.codes.ok:
        return HttpResponse(html, status=404)

    return HttpResponse(html)


def people(request, handle):
    status_code, html = grab_page("/people/" + handle)

    if status_code != requests.codes.ok:
        return HttpResponse(html, status=404)

    return HttpResponse(html)


def follow_confirm(request):
    print(request)

    # follow question
    if "question" in request.POST:
        # TODO
        Question.objects.get

    # follow person
    if "people" in request.POST:
        # TODO
        People.objects.get

    return HttpResponse()
