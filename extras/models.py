from django.db import models
from django.contrib.auth.models import User

from ordered_model.models import OrderedModel

from listing.models import Comic, Issue


class ReadIssue(models.Model):
    user = models.ForeignKey(User, related_name='read')
    issue = models.ForeignKey(Issue, related_name='users')
    count = models.IntegerField(default=0)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user']


class Playlist(models.Model):
    title = models.CharField(max_length=200)
    items = models.ManyToManyField(Issue, through='PlaylistItem')
    creator = models.ForeignKey(User, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)


class PlaylistItem(OrderedModel):
    issue = models.ForeignKey(Issue)
    playlist = models.ForeignKey(Playlist)
    order_with_respect_to = 'playlist'

    class Meta(OrderedModel.Meta):
        pass
