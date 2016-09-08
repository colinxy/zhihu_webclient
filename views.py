
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.http import require_safe
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.utils.decorators import method_decorator
import requests
import json

from .models import Question, People
from .zhihu_util import (grab_page, check_follow_request,
                         check_unfollow_request)


@require_safe
def index(request):
    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.order_by("name"),
        "people_following": People.objects.order_by("name"),
    })


@require_safe
def search(request):
    status_code, html_str = grab_page("/search", request.GET)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


@require_safe
def topic(request, topic_id):
    status_code, html_str = grab_page("/topic/" + topic_id)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


class QuestionView(View):
    def get(self, request, question_id):
        status_code, html_str = grab_page("/question/" + question_id)
        if status_code != requests.codes.ok:
            return HttpResponse(html_str, status=404)

        return HttpResponse(html_str)

    def post(self, request, question_id):
        "follow question"
        try:
            payload = json.loads(request.body.decode("utf-8"))
            question_name = payload["name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        try:
            Question.objects.get(question_id=question_id)
        except ObjectDoesNotExist:
            Question.objects.create(question_id=question_id,
                                    name=question_name)

        return HttpResponse(content_type="application/json")

    def delete(self, request, question_id):
        "unfollow question"
        try:
            q = Question.objects.get(question_id=question_id)
            q.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(QuestionView, self).dispatch(*args, **kwargs)


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


class PeopleView(View):
    def get(self, request, handle):
        status_code, html_str = grab_page("/people/" + handle)
        if status_code != requests.codes.ok:
            return HttpResponse(html_str, status=404)

        return HttpResponse(html_str)

    def post(self, request, handle):
        "follow people"
        try:
            payload = json.loads(request.body.decode("utf-8"))
            name = payload["name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        try:
            People.objects.get(handle=handle)
        except ObjectDoesNotExist:
            People.objects.create(handle=handle, name=name)

        return HttpResponse(content_type="application/json")

    def delete(self, request, handle):
        "unfollow people"
        try:
            p = People.objects.get(handle=handle)
            p.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(QuestionView, self).dispatch(*args, **kwargs)


@ensure_csrf_cookie
def people(request, handle):
    status_code, html_str = grab_page("/people/" + handle)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


def follow_confirm(request):
    try:
        payload_type, payload = check_follow_request(request)
    except AttributeError as ex:
        print(ex)
        return HttpResponse(content_type="application/json", status=400)

    print(payload)
    # follow question
    if "question" == payload_type:
        try:
            Question.objects.get(question_id=payload["question"])
        except ObjectDoesNotExist:
            Question.objects.create(question_id=payload["question"],
                                    name=payload["name"])
    # follow person
    elif "people" == payload_type:
        try:
            People.objects.get(handle=payload["people"])
        except ObjectDoesNotExist:
            People.objects.create(handle=payload["people"],
                                  name=payload["name"])

    return HttpResponse(content_type="application/json")


def unfollow_confirm(request):
    try:
        payload_type, payload = check_unfollow_request(request)
    except AttributeError as ex:
        print(ex)
        return HttpResponse(content_type="application/json", status=400)

    print(payload)
    try:
        # delete question
        if "question" == payload_type:
            q = Question.objects.get(question_id=payload["question"])
            q.delete()
        # delete people
        elif "people" == payload_type:
            p = People.objects.get(handle=payload["people"])
            p.delete()
    except ObjectDoesNotExist as ex:
        return HttpResponse(content_type="application/json", status=400)

    return HttpResponse(content_type="application/json")
