from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^issue/(?P<comic_id>[0-9]+)/(?P<issue_id>[0-9]+)/$', views.read_issue, name='read_issue'),
    url(r'^mine/$', views.my_read, name='my_read')
]