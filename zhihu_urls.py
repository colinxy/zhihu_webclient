from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^question/(?P<question_id>[0-9]+)/?$",
        views.QuestionView.as_view(), name="question"),
    url(r"^question/(?P<question_id>[0-9]+)/answer/(?P<answer_id>[0-9]+)/?$",
        views.AnswerView.as_view(), name="answer"),
    url(r"^people/(?P<handle>[\w\d\-_]+)/?",
        views.PeopleView.as_view(), name="people"),
    url(r"^topic/(?P<topic_id>[0-9]+)/?",
        views.topic, name="topic"),
    url(r"^search$",
        views.search, name="search"),
]
