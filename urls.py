from django.conf.urls import url, include
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views

from . import views

app_name = 'client'
urlpatterns = [
    url(r'^$', views.index, name="index"),

    url(r'^accounts/register/', views.RegisterView.as_view(),
        name="register"),
    url(r'accounts/login/', auth_views.login, {
        "template_name": "registration/login.djhtml"
    }, name="login"),
    url(r'accounts/logout/', auth_views.logout, {
        "next_page": "/"
    }, name="logout"),

    url(r"^", include("client.zhihu_urls")),
]
