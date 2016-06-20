import re


def get_url(id, title='title', all=True):
    if all:
        url = "http://marvel.com/comics/series/{id}/{title}?offset=0&orderBy=release_date+asc&byId={id}&totalcount=10000"
    else:
        url = "http://marvel.com/comics/series/{id}/{title}"
    url = url.format(id=id, title=title)
    return url


def parse_title(name):
    rx = re.search(r'(.*) \((\d{4})(?: -? (\d{4}|Present))?\)', name)
    if rx:
        parsed = rx.groups()
        if parsed[-1] is None:
            years = (parsed[1], -1)
        else:
            years = (parsed[1], (0 if parsed[2] == 'Present' else parsed[2]))

        years = tuple(int(y) for y in years)

        return (parsed[0], years)



def parse_name(name):
    if ',' in name:
        split = [str.strip() for str in name.split(',')]
        # return ' '.join([split[-1], split[0]])
        return [split[-1], split[0]]
    else:
        return [name]
