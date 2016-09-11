
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.http import require_safe
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils import timezone
import requests
import json

from .models import Question, People, Answer
from .zhihu_util import grab_page


@require_safe
def index(request):
    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.order_by("-date_added"),
        "people_following": People.objects.order_by("-date_added"),
        "answer_following": Answer.objects.order_by("-date_added"),
    })


@require_safe
def search(request):
    status_code, html_str = grab_page("/search", "search", request.GET)

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


@require_safe
def topic(request, topic_id):
    # additional features of topic not implemented
    status_code, html_str = grab_page(request.path, "topic")

    if status_code != requests.codes.ok:
        return HttpResponse(html_str, status=404)

    resp = HttpResponse(html_str)
    return resp


class QuestionView(View):
    def get(self, request, question_id):
        status_code, html_str = grab_page("/question/" + question_id,
                                          "question")
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
                                    name=question_name,
                                    date_added=timezone.now())

        return HttpResponse(content_type="application/json")

    def delete(self, request, question_id):
        "unfollow question"
        # CAVEAT : get rid of a question would
        # get rid of all its corresponding answers
        try:
            q = Question.objects.get(question_id=question_id)
            # delete all corresponding answers
            Answer.objects.filter(question=q).delete()
            # delete question
            q.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(QuestionView, self).dispatch(*args, **kwargs)


class AnswerView(View):
    def get(self, request, question_id, answer_id):
        status_code, html_str = grab_page("/question/" + question_id +
                                          "/answer/" + answer_id,
                                          "answer")

        if status_code != requests.codes.ok:
            return HttpResponse(html_str, status=404)

        return HttpResponse(html_str)

    def post(self, request, question_id, answer_id):
        "follow question"
        try:
            payload = json.loads(request.body.decode("utf-8"))
            question_name = payload["name"]
            author_name = payload["author_name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        # first create question if it does not exist
        try:
            q = Question.objects.get(question_id=question_id)
        except ObjectDoesNotExist:
            q = Question.objects.create(question_id=question_id,
                                        name=question_name,
                                        date_added=timezone.now())
        # then create corresponding answer
        try:
            Answer.objects.get(answer_id=answer_id, question=q)
        except ObjectDoesNotExist:
            Answer.objects.create(answer_id=answer_id, question=q,
                                  author_name=author_name,
                                  date_added=timezone.now())

        return HttpResponse(content_type="application/json")

    def delete(self, request, question_id, answer_id):
        "unfollow answer"
        try:
            ans = Answer.objects.get(answer_id=answer_id)
            ans.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(AnswerView, self).dispatch(*args, **kwargs)


class PeopleView(View):
    def get(self, request, handle):
        # additional features of topic not implemented
        status_code, html_str = grab_page(request.path, "people", request.GET)
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
            People.objects.create(handle=handle, name=name,
                                  date_added=timezone.now())

        return HttpResponse(content_type="application/json")

    def delete(self, request, handle):
        "unfollow people"
        try:
            p = People.objects.get(handle=handle)
            p.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(PeopleView, self).dispatch(*args, **kwargs)
