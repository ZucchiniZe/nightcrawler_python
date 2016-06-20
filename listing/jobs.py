from django_rq import job

import re
import requests
import uuid
import analytics
from lxml import html, etree
from datetime import datetime

from haystack import connection_router, connections
from .models import Comic, Issue, Creator
from .helpers import get_url, parse_name, parse_title

analytics.write_key = '3jPlLTLsajh0UoIfYq3L95EdiErVaZ57'


@job('high')
def scrape_issues(data, comic):
    url = get_url(data)

    page = requests.get(url)
    tree = html.fromstring(page.content)

    containers = [etree.tostring(row)
                  for row in tree.xpath('//div[@class="row-item comic-item"]/div[@class="row-item-text"]')]
    dicts = []

    for container in containers:
        data = {}
        tree = html.fromstring(container)

        data['title'] = tree.xpath('//h5/a/text()')[0].strip()

        data['link'] = tree.xpath('//a[@class="see-inside"]/@href') or None
        if data['link'] is not None:
            data['link'] = data['link'][0]
            data['id'] = int(data['link'].split('/')[-1])
        else:
            data['id'] = None

        if '#' in data['title']:
            rx = re.match('^.*#(\d*.\d*)$', data['title'])
            if rx:
                data['num'] = float(rx.groups()[0])
        else:
            data['num'] = None

        if data['link'] is not None:
            dicts.append(data)

        data['creators'] = []
        for creator_container in [etree.tostring(row) for row in tree.xpath('//p[@class="meta-creators"]/a')]:
            tree = html.fromstring(creator_container)

            creator = dict(name=tree.xpath('//text()')[0].strip(), id=tree.xpath('//@href')[0].split('/')[-2])

            data['creators'].append(creator)

    # code for saving the results
    for result in dicts:
        creators = result.pop('creators')
        issue = Issue(comic=comic, **result)
        issue.save()

        for creator in creators:
            del creator['name']
            c, created = Creator.objects.get_or_create(**creator)
            c.issues.add(issue)
            c.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Issues', {
        'series': comic.title,
        'timestamp': datetime.now()
    })
    comic.scraped = True
    comic.save()

    return 'Scraped and imported {} issues for {}'.format(len(dicts), comic.title)


@job('high')
def scrape_comics():
    url = "http://marvel.com/comics/series"

    page = requests.get(url)
    tree = html.fromstring(page.content)

    titles_titles = tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/text()")
    urls = tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/@href")
    ids = list(map(lambda s: int(s.split('/')[3]), urls))

    titles = [parse_title(title) for title in titles_titles]

    both = [(a, b, c) for (a, b), c in zip(titles, ids)]

    dicts = [{'title': cur[0], 'start': cur[1][0], 'end': cur[1][1], 'id': cur[2], 'scraped': False} for cur in both]

    for result in dicts:
        comic = Comic(**result)
        comic.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Titles', {
        'timestamp': datetime.now()
    })

    return 'Scraped and imported {} comics'.format(len(dicts))


@job('high')
def scrape_creators():
    url = "http://marvel.com/comics/creators"

    page = requests.get(url)
    tree = html.fromstring(page.content)

    names = [parse_name(name) for name in tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/text()")]
    urls = tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/@href")
    ids = list(map(lambda s: int(s.split('/')[3]), urls))
    full_urls = [str('http://marvel.com' + url) for url in urls]

    dicts = []
    for cur in zip(names, full_urls, ids):
        if len(cur[0]) == 2:
            dicts.append({'first': cur[0][0], 'last': cur[0][1], 'url': cur[1], 'id': cur[2]})
        else:
            dicts.append({'first': cur[0][0], 'last': '', 'url': cur[1], 'id': cur[2]})

    for result in dicts:
        creator = Creator(**result)
        creator.save()

    analytics.track(str(uuid.uuid4()), 'Refresh Creators', {
        'timestamp': datetime.now()
    })

    return 'Scraped and imported {} creators'.format(len(dicts))


@job('low')
def index_object(sender, instance):
    backends = connection_router.for_write(instance=instance)

    for backend in backends:
        index = connections[backend].get_unified_index().get_index(sender)
        index.update_object(instance, using=backend)
