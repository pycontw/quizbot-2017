from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.fb_webhook),
    url(r'^leaderboard/$', views.leaderboard)
]
