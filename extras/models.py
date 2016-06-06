from django.db import models
from django.contrib.auth.models import User

from listing.models import Issue


class ReadIssue(models.Model):
    user = models.ForeignKey(User, related_name='read')
    issue = models.ForeignKey(Issue, related_name='users')
    count = models.IntegerField(default=0)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user']
        index_together = ['user', 'issue']