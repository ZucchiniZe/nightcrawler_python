import uuid
import analytics
from datetime import datetime

from .models import Comic, Issue, Creator

analytics.write_key = '3jPlLTLsajh0UoIfYq3L95EdiErVaZ57'


def import_titles(task):
    results = task.result
    for result in results:
        comic = Comic(**result)
        comic.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Titles', {
        'timestamp': datetime.now()
    })


def import_issues(task):
    results, comic = task.result
    for result in results:
        creators = result.pop('creators')
        issue = Issue(comic=comic, **result)

        for creator in creators:
            del creator['name']
            c, created = Creator.objects.get_or_create(**creator)
            c.issues.add(issue)
            c.save()

        issue.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Issues', {
        'series': comic.title,
        'timestamp': datetime.now()
    })
    comic.scraped = True
    comic.save()


def import_creators(task):
    results = task.result
    for result in results:
        creator = Creator(**result)
        creator.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Creators', {
        'timestamp': datetime.now()
    })
