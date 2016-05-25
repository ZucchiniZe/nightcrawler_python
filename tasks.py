import uuid
import analytics
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from scrape import *
from db import *

analytics.write_key = '3jPlLTLsajh0UoIfYq3L95EdiErVaZ57'

def import_issues(title_id):
    db.connect()
    comic = Comic.get(Comic.id == title_id)
    analytics.track(str(uuid.uuid4()), 'Refresh Issues', {
        'series': comic.title,
        'timestamp': datetime.now()
    })
    issues = scrape_issues(model_to_dict(comic))
    issues = list(map(lambda x: dict({'series': comic}, **x), issues))

    with db.atomic():
        for idx in range(0, len(issues), 199):
            Issue.insert_many(issues[idx:idx+199]).execute()

    Comic.update(scraped=True, refreshed_at=datetime.now()).where(Comic.id == title_id).execute()
    db.close()

def import_titles():
    db.connect()
    analytics.track(str(uuid.uuid4()), 'Refresh Titles', {
        'timestamp': datetime.now()
    })
    Comic.delete().execute()
    titles = scrape_titles()
    titles = list(map(lambda x: dict({'search_title': fn.to_tsvector(x['title'])}, **x), titles))

    with db.atomic():
        for idx in range(0, len(titles), 150):
            Comic.insert_many(titles[idx:idx+150]).execute()

    db.close()
