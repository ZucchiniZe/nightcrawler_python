from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async

from .tasks import get_url, index_object


class Comic(models.Model):
    title = models.CharField(max_length=200)
    start = models.IntegerField()
    end = models.IntegerField()
    scraped = models.BooleanField()
    refreshed_at = models.DateTimeField(auto_now=True)

    @property
    def run(self):
        if self.end is -1:
            return str(self.start)
        elif self.end is 0:
            return "{} - Present".format(self.start)
        else:
            return "{} - {}".format(self.start, self.end)

    @property
    def issue_count(self):
        return self.issues.count()

    @property
    def url(self):
        return get_url(self.id, title=self.title, all=False)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('listing:comic', args=(self.id,))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Issue(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    num = models.FloatField(blank=True, null=True)
    comic = models.ForeignKey(Comic, related_name='issues')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('listing:issue', args=(self.id,))

    def was_read_by(self, user):
        return bool(self.users.filter(user=user).count())

    class Meta:
        ordering = ['num']


class Creator(models.Model):
    first = models.CharField(max_length=100)
    last = models.CharField(blank=True, max_length=100)
    url = models.URLField(default='http://marvel.com/comics/creators')
    issues = models.ManyToManyField(Issue, related_name='creators')

    @property
    def name(self):
        if self.last:
            return "{} {}".format(self.first, self.last)
        else:
            return self.first

    @property
    def published_issues(self):
        return self.issues.count()

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('listing:creator', args=(self.id,))

    class Meta:
        ordering = ['first']


@receiver(post_save, sender=Creator)
@receiver(post_save, sender=Comic)
@receiver(post_save, sender=Issue)
def object_changed(sender, instance, **kwargs):
    async(index_object, sender, instance, save=False)
