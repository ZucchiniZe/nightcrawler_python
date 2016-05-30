from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^comics/$', views.listing, name='listing'),
    url(r'^synced/$', views.synced, name='synced'),
    url(r'^comic/(?P<pk>[0-9]+)/$', views.comic, name='comic'),
    url(r'^issue/(?P<pk>[0-9]+)/$', views.issue, name='issue'),
    url(r'^creator/(?P<pk>[0-9]+)/$', views.creator, name='creator'),
    url(r'^refresh/comics/$', views.refresh_comics, name='refresh_comics'),
    url(r'^refresh/issues/(?P<pk>[0-9]+)/$', views.refresh_issues, name='refresh_issues'),
]
