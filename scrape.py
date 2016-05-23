from lxml import html, etree
from parse import parse
import requests

def get_url(data):
    url = "http://marvel.com/comics/series/{id}/{title}?offset=0&orderBy=release_date+asc&byId={id}&totalcount=10000".format(id=data['id'], title=data['title'])
    return url

def scrape_issues(data):
    url = get_url(data)

    page = requests.get(url)
    tree = html.fromstring(page.content)

    containers = [etree.tostring(row) for row in tree.xpath('//div[@class="row-item comic-item"]/div[@class="row-item-text"]')]
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

    return dicts

# print(scrape_issues({'title': 'Ant-Man', 'id': 2258}))

def parse_title(name):
    years = name.rsplit('(', 1)[1][:-1]
    parsed = None
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

# parse_title("X-Men Origins: Wolverine (2013 - 2015)")
# parse_title("Deadpool (2010)")
# parse_title("Avengers (2012 - Present)")

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

# print(scrape_titles())
