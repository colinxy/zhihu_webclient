
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils import timezone
from django.views.decorators.http import require_safe
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View
from django.views.generic.edit import FormView
import requests
import json

from .models import Question, People, Answer
from .zhihu_util import grab_page


@require_safe
def index(request):
    if not request.user.is_authenticated():
        return render(request, "client/index.djhtml", {
            "question_following": [],
            "people_following": [],
            "answer_following": []
        })

    return render(request, "client/index.djhtml", {
        "question_following": Question.objects.
        filter(user=request.user).order_by("-date_added"),
        "people_following": People.objects.
        filter(user=request.user).order_by("-date_added"),
        "answer_following": Answer.objects.
        filter(user=request.user).order_by("-date_added"),
    })


class RegisterView(FormView):
    template_name = "registration/signup.djhtml"
    form_class = UserCreationForm
    success_url = "/"

    def form_valid(self, form):
        form.save()             # save to db

        new_user = authenticate(username=form.cleaned_data["username"],
                                password=form.cleaned_data["password1"])
        login(self.request, new_user)
        return super(RegisterView, self).form_valid(form)


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
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            payload = json.loads(request.body.decode("utf-8"))
            question_name = payload["name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        try:
            Question.objects.get(question_id=question_id, user=request.user)
        except ObjectDoesNotExist:
            Question.objects.create(question_id=question_id,
                                    name=question_name,
                                    date_added=timezone.now(),
                                    user=request.user)

        return HttpResponse(content_type="application/json")

    def delete(self, request, question_id):
        "unfollow question"
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            q = Question.objects.get(question_id=question_id,
                                     user=request.user)
            # delete question
            # delete all corresponding answers, on_delete=CASCADE
            q.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    def redirect_login(self):
        resp = {"url": "{}?next={}".format(reverse('client:question'),
                                           urlencode(self.request.path))}
        return HttpResponse(json.dumps(resp),
                            content_type="application/json")

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
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            payload = json.loads(request.body.decode("utf-8"))
            question_name = payload["name"]
            author_name = payload["author_name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        # first create question if it does not exist
        try:
            q = Question.objects.get(question_id=question_id,
                                     user=request.user)
        except ObjectDoesNotExist:
            q = Question.objects.create(question_id=question_id,
                                        name=question_name,
                                        date_added=timezone.now(),
                                        user=request.user)
        # then create corresponding answer
        try:
            Answer.objects.get(answer_id=answer_id, question=q)
        except ObjectDoesNotExist:
            Answer.objects.create(answer_id=answer_id, question=q,
                                  author_name=author_name,
                                  date_added=timezone.now(),
                                  user=request.user)

        return HttpResponse(content_type="application/json")

    def delete(self, request, question_id, answer_id):
        "unfollow answer"
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            q = Question.objects.get(question_id=question_id,
                                     username=request.user)
            ans = Answer.objects.get(question=q, answer_id=answer_id)
            ans.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    def redirect_login(self):
        resp = {"url": "{}?next={}".format(reverse('client:answer'),
                                           urlencode(self.request.path))}
        return HttpResponse(json.dumps(resp),
                            content_type="application/json")

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
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            payload = json.loads(request.body.decode("utf-8"))
            name = payload["name"]
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest(content_type="application/json")

        try:
            People.objects.get(handle=handle, user=request.user)
        except ObjectDoesNotExist:
            People.objects.create(handle=handle, name=name,
                                  date_added=timezone.now(),
                                  user=request.user)

        return HttpResponse(content_type="application/json")

    def delete(self, request, handle):
        "unfollow people"
        if not request.user.is_authenticated():
            return self.redirect_login()

        try:
            p = People.objects.get(handle=handle, user=request.user)
            p.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(content_type="application/json")

        return HttpResponse(content_type="application/json")

    def redirect_login(self):
        resp = {"url": "{}?next={}".format(reverse('client:people'),
                                           urlencode(self.request.path))}
        return HttpResponse(json.dumps(resp),
                            content_type="application/json")

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(PeopleView, self).dispatch(*args, **kwargs)
