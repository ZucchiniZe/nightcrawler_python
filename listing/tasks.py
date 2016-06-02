from lxml import html, etree
from parse import parse
import requests

from haystack import connection_router, connections


def get_url(id, title='title', all=True):
    if all:
        url = "http://marvel.com/comics/series/{id}/{title}?offset=0&orderBy=release_date+asc&byId={id}&totalcount=10000"
    else:
        url = "http://marvel.com/comics/series/{id}/{title}"
    url = url.format(id=id, title=title)
    return url


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
            data['num'] = float(parse('{} #{}', data['title'])[-1])
        else:
            data['num'] = None

        if data['link'] is not None:
            dicts.append(data)

        data['creators'] = []
        for container in [etree.tostring(row) for row in tree.xpath('//p[@class="meta-creators"]/a')]:
            tree = html.fromstring(container)

            creator = dict(name=tree.xpath('//text()')[0].strip(), id=tree.xpath('//@href')[0].split('/')[-2])

            data['creators'].append(creator)

    return dicts, comic


def parse_title(name):
    years = name.rsplit('(', 1)[1][:-1]
    if '-' in years:
        parsed = parse("{} ({:d} - {})", name)
    else:
        parsed = parse("{} ({:d})", name)

    parsed = list(parsed)
    data = None

    if len(parsed) >= 3:
        title = parsed[0]
        year1 = parsed[1]
        year2 = parsed[2]
        data = (title, (year1, (0 if year2 == 'Present' else year2)))
    elif len(parsed) >= 2:
        title = parsed[0]
        year = parsed[1]
        data = (title, (year, -1))
    return data


def scrape_titles():
    url = "http://marvel.com/comics/series"

    page = requests.get(url)
    tree = html.fromstring(page.content)

    titles_titles = tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/text()")
    urls = tree.xpath("//div//ul[@class='JCAZList-MultiCol']/li//a/@href")
    ids = list(map(lambda s: int(s.split('/')[3]), urls))

    titles = [parse_title(title) for title in titles_titles]

    both = [(a, b, c) for (a, b), c in zip(titles, ids)]

    dicts = [{'title': cur[0], 'start': cur[1][0], 'end': cur[1][1], 'id': cur[2], 'scraped': False} for cur in both]

    return dicts


def parse_name(name):
    if ',' in name:
        split = [str.strip() for str in name.split(',')]
        # return ' '.join([split[-1], split[0]])
        return [split[-1], split[0]]
    else:
        return [name]

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

    return dicts


def index_object(sender, instance):
    backends = connection_router.for_write(instance=instance)

    for backend in backends:
        index = connections[backend].get_unified_index().get_index(sender)
        index.update_object(instance, using=backend)