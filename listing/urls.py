from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^comics/$', views.AllTitleView.as_view(), name='listing'),
    url(r'^titles/$', views.AllTitleView.as_view(), name='titles'),
    url(r'^synced/$', views.SyncedView.as_view(), name='synced'),
    url(r'^creators/$', views.AllCreatorView.as_view(), name='creators'),
    url(r'^comic/(?P<pk>[0-9]+)/$', views.comic_view, name='comic'),
    # url(r'^title/(?P<pk>[0-9]+)/$', views.ComicView.as_view(), name='title'),
    url(r'^issue/(?P<pk>[0-9]+)/$', views.IssueView.as_view(), name='issue'),
    url(r'^creator/(?P<pk>[0-9]+)/$', views.CreatorView.as_view(), name='creator'),
    url(r'^refresh/comics/$', views.refresh_comics, name='refresh_comics'),
    url(r'^refresh/creators/$', views.refresh_creators, name='refresh_creators'),
    url(r'^refresh/issues/(?P<pk>[0-9]+)/$', views.refresh_issues, name='refresh_issues'),
    url(r'^search/$', views.search, name='search')
]
