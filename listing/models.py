from django.db import models


class Comic(models.Model):
    title = models.CharField(max_length=200)
    start = models.IntegerField()
    end = models.IntegerField()
    scraped = models.BooleanField()
    refreshed_at = models.DateTimeField(auto_now=True)
    # maybe some search field here if possible

    def run(self):
        if self.end is -1:
            return self.start
        elif self.end is 0:
            return "{} - Present".format(self.start)
        else:
            return "{} - {}".format(self.start, self.end)

    def issues(self):
        return self.issue_set.count()

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    num = models.FloatField(blank=True)
    comic = models.ForeignKey(Comic)

    def __str__(self):
        return self.title


class Creator(models.Model):
    first = models.CharField(max_length=100)
    last = models.CharField(blank=True, max_length=100)
    issues = models.ManyToManyField(Issue)

    def name(self):
        if self.last:
            return "{} {}".format(self.first, self.last)
        else:
            return self.first

    def published_issues(self):
        return self.issues.count()

    def __str__(self):
        return "{} {}".format(self.first, self.last)
