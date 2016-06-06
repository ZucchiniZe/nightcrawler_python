from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^read/issue/(?P<comic_id>[0-9]+)/(?P<issue_id>[0-9]+)/$', views.read_issue, name='read_issue'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.profile, name='profile'),
    url(r'^playlists/$', views.PlaylistListView.as_view(), name='playlists'),
    url(r'^playlist/(?P<pk>[0-9]+)/$', views.PlaylistView.as_view(), name='playlist'),
    url(r'^playlist/(?P<pk>[0-9]+)/edit/$', views.edit_playlist, name='playlist'),
    url(r'^api/issue/search/$', views.search_issues, name='issue_search'),
]