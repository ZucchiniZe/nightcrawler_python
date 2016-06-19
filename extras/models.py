from django.db import models
from django.contrib.auth.models import User

from ordered_model.models import OrderedModel

from listing.models import Comic, Issue


class ReadIssue(models.Model):
    user = models.ForeignKey(User, related_name='reads')
    issue = models.ForeignKey(Issue, related_name='users')
    count = models.IntegerField(default=1)
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "U{} I{} C{}".format(self.user.id, self.issue.id, self.count)

    class Meta:
        ordering = ['user']
        index_together = ['user', 'issue']


class Playlist(models.Model):
    title = models.CharField(max_length=200)
    items = models.ManyToManyField(Issue, through='PlaylistItem')
    creator = models.ForeignKey(User, related_name='playlists')
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created_at',)


class PlaylistItem(OrderedModel):
    issue = models.ForeignKey(Issue)
    playlist = models.ForeignKey(Playlist)
    order_with_respect_to = 'playlist'

    def __str__(self):
        return "I{} P{} O{}".format(self.issue.id, self.playlist.id, self.order)

    class Meta:
        ordering = ('playlist', 'order')
