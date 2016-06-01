from django.test import TestCase

from .models import Comic, Issue, Creator


class ComicTestCase(TestCase):
    def setUp(self):
        with_issues = Comic(title='Lean mean meme machine', start=2016, end=0, scraped=False)
        with_issues.save()

        everest = Comic(title='1602: Everest', start=2011, end=-1, scraped=False)
        everest.save()
        tumber = Comic(title='Tumber Survey', start=2014, end=2016, scraped=False).save()

        everest_issue = Issue(title='1602: Everest #1', link='http://wiki.alexb.io', num=1)
        everest_issue.comic = everest
        everest_issue.save()

        first_issue = Issue(title='Lean mean meme machine #1', link='http://app.mysummitps.org', num=1)
        first_issue.comic = with_issues
        first_issue.save()

        second_issue = Issue(title='Learn mean meme machine #2', link='http://google.com/#q=everest+scandals', num=2)
        second_issue.comic = with_issues
        second_issue.save()

    def test_comic_run_length(self):
        current_comic = Comic.objects.get(title='Lean mean meme machine')
        old_comic = Comic.objects.get(title='1602: Everest')
        full_comic = Comic.objects.get(title='Tumber Survey')
        self.assertEqual(current_comic.run, '2016 - Present')
        self.assertEqual(old_comic.run, '2011')
        self.assertEqual(full_comic.run, '2014 - 2016')

    def test_comic_current_issues(self):
        single = Comic.objects.get(title='1602: Everest')
        double = Comic.objects.get(title='Lean mean meme machine')
        self.assertEqual(single.issues, 1)
        self.assertEqual(double.issues, 2)
