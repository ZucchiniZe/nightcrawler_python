from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^read/issue/(?P<comic_id>[0-9]+)/(?P<issue_id>[0-9]+)/$', views.read_issue, name='read_issue'),
    url(r'^read/mine/$', views.my_read, name='my_read'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.profile, name='profile'),
]