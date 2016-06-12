from django.test import TestCase
from django.contrib.auth.models import User

from extras.models import ReadIssue
from .models import Comic, Issue, Creator
from .tasks import get_url


class ComicTest(TestCase):
    def setUp(self):
        self.with_issues = Comic.objects.create(title='Lean mean meme machine', start=2016, end=0,
                                                scraped=False, id=0)

        self.everest = Comic.objects.create(title='1602: Everest', start=2011, end=-1,
                                            scraped=False, id=1243)

        self.tumber = Comic.objects.create(title='Tumber Survey', start=2014, end=2016,
                                           scraped=False, id=2)

        Issue.objects.create(title='1602: Everest #1', link='http://wiki.alexb.io',
                             num=1, comic=self.everest)

        Issue.objects.create(title='Lean mean meme machine #1', link='http://app.mysummitps.org',
                             num=1, comic=self.with_issues)

        Issue.objects.create(title='Learn mean meme machine #2', link='http://google.com/#q=everest+scandals',
                             num=2, comic=self.with_issues)

    def test_comic_model(self):
        self.assertEqual(self.everest.title, '1602: Everest')
        self.assertEqual(self.everest.start, 2011)
        self.assertEqual(self.everest.end, -1)
        self.assertEqual(self.everest.scraped, False)
        self.assertEqual(self.everest.id, 1243)

    def test_comic_str_(self):
        self.assertEqual(str(self.everest), '1602: Everest')

    def test_comic_run_length(self):
        self.assertEqual(self.with_issues.run, '2016 - Present')
        self.assertEqual(self.everest.run, '2011')
        self.assertEqual(self.tumber.run, '2014 - 2016')

    def test_comic_current_issue_count(self):
        self.assertEqual(self.everest.issue_count, 1)
        self.assertEqual(self.with_issues.issue_count, 2)

    def test_comic_url(self):
        self.assertEqual(self.tumber.url, 'http://marvel.com/comics/series/2/Tumber Survey')
        self.assertEqual(self.everest.url, 'http://marvel.com/comics/series/1243/1602: Everest')


class IssueTest(TestCase):
    def setUp(self):
        self.me = User.objects.create_user('me', password='superpass')
        hc = Comic.objects.create(title='Hack Club', start=2014, end=0, scraped=True)

        self.issue = Issue.objects.create(title='Hack Club #1', link='https://hackclub.com', num=1, comic=hc)

        ReadIssue.objects.create(issue=self.issue, user=self.me)

    def test_issue_str(self):
        self.assertEqual(str(self.issue), 'Hack Club #1')

    def test_was_read_by(self):
        self.assertEqual(self.issue.was_read_by(self.me), True)


class CreatorTest(TestCase):
    def setUp(self):
        pass


class TaskTest(TestCase):
    def test_get_url(self):
        all = get_url(1, 'test', all=True)
        some = get_url(1, 'test', all=False)
        self.assertEqual(all, 'http://marvel.com/comics/series/1/test?offset=0&orderBy=release_date+asc&byId=1&totalcount=10000')
        self.assertEqual(some, 'http://marvel.com/comics/series/1/test')
