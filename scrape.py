from lxml import html
from parse import parse
import requests

def get_url(data):
    url = "http://marvel.com/comics/series/{id}/{title}?offset=0&orderBy=release_date+asc&byId={id}&totalcount=10000".format(id=data['id'], title=data['title'])
    return url

def scrape_issues(data):
    url = get_url(data)

    page = requests.get(url)
    tree = html.fromstring(page.content)

    titles = [x.strip() for x in tree.xpath('//div[@class="row-item comic-item"]/div[@class="row-item-text"]/h5/a[@class="meta-title"]/text()')]
    links = tree.xpath('//div[@class="row-item comic-item"]/div[@class="row-item-text"]/a[@class="see-inside"]/@href')
    ids = list(map(lambda s: int(s.split('/')[-1]), links))
    nums = []
    for title in titles:
        if '#' in title:
            nums.append(float(parse("{} #{}", title)[-1]))
        else:
            nums.append(None)
    # nums = list(map(lambda s: int(parse("{} #{}", s)[-1]), titles))


    both = list(zip(titles, links, ids, nums))
    dicts = [{'title': cur[0], 'link': cur[1], 'id': cur[2], 'num': cur[3]} for cur in both]

    return dicts

# print(scrape_issues({'title': 'Ant-Man', 'id': 16451}))

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
# parse_title("Ms. Marvel (2006 - 2010)")
# parse_title("Halo: Fall of Reach - Invasion (2010 - 2012)")

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
