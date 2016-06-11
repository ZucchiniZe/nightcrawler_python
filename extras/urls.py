from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^read/issue/(?P<comic_id>[0-9]+)/(?P<issue_id>[0-9]+)/$', views.read_issue, name='read_issue'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.profile, name='profile'),
    url(r'^playlists/$', views.PlaylistListView.as_view(), name='playlists'),
    url(r'^playlist/create/$', views.edit_playlist, name='create_playlist'),
    url(r'^playlist/(?P<pk>[0-9]+)/$', views.PlaylistView.as_view(), name='playlist'),
    url(r'^playlist/(?P<pk>[0-9]+)/edit/$', views.edit_playlist, name='playlist_edit'),
    url(r'^api/issue/search/$', views.search_issues, name='issue_search'),
    url(r'^api/comic/search/$', views.search_comics, name='comic_search'),
    url(r'^api/comic/(?P<pk>[0-9]+)/issues/$', views.get_issues_comic, name='comic_issues'),
]