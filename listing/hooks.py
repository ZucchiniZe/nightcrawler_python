import uuid
import analytics
from datetime import datetime

from .models import Comic, Issue, Creator

analytics.write_key = '3jPlLTLsajh0UoIfYq3L95EdiErVaZ57'


def import_titles(task):
    results = task.result
    comics = []
    for result in results:
        comic = Comic(**result)
        comics.append(comic)

    Comic.objects.bulk_create(comics)

    analytics.track(str(uuid.uuid4()), 'Refresh Titles', {
        'timestamp': datetime.now()
    })


def import_issues(task):
    results, comic = task.result
    for result in results:
        issue = Issue(comic=comic, **result)
        issue.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Issues', {
        'series': comic.title,
        'timestamp': datetime.now()
    })
    comic.scraped = True
    comic.save()


