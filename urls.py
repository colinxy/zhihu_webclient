from django.conf.urls import url, include

from . import views

app_name = 'client'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    # url(r"^follow", views.follow_confirm),
    # url(r"^unfollow", views.unfollow_confirm),
    # url(r'^login/', ),
    url(r"^", include("client.zhihu_urls")),
]
