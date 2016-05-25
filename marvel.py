# -*- coding: utf-8 -*-

# ALL THE IMPORTS!
import rq_dashboard
from flask import Flask, request, g, redirect, url_for, render_template, flash
from flask.ext.cache import Cache
from urllib.parse import urlparse
from werkzeug.contrib.cache import RedisCache
from time import process_time
from playhouse.shortcuts import model_to_dict
from opbeat.contrib.flask import Opbeat
from redis import Redis
from rq import Queue
from db import *
from tasks import *

app = Flask(__name__)

app.secret_key = 'sekrit'

redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
url = urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

q = Queue(connection=conn)

app.config.from_object(rq_dashboard.default_settings)
app.config.update(REDIS_URL=redis_url)
app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')

cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'cache',
    'CACHE_REDIS_URL': redis_url
}

cache = Cache(app, config=cache_config)

opbeat = Opbeat(
    app,
    organization_id='e4a92e8bae9a4cd9b82ad1ccb4f09f83',
    app_id='10c2a61210',
    secret_token='fb88ac5a782f33e09260b785b650cfff98df5c1f',
)

def init_db():
    db.connect()
    db.create_tables([Comic, Issue])
    db.close()

app.jinja_env.globals.update(get_url=get_url)

@app.template_filter('scraped')
def bool_filter(scraped):
    if scraped:
        return u"✓"
    else:
        return u"✗"

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    if number == 1: return singular
    else: return plural

@app.template_filter('parseyear')
def parse_year(year):
    if year == 0: return 'Present'
    return year

@app.before_request
def before_request():
    g.db = db
    g.db.connect()
    if 'nightcrawler-m.herokuapp.com' in request.headers.get('Host'):
        return redirect('http://nightcrawler.us' + request.path, code=301)

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')
def show_front():
    return render_template('frontpage.html')

@cache.cached(timeout=300)
@app.route('/titles')
def show_titles():
    titles = (Comic
              .select()
              .order_by(Comic.title)
              .dicts())
    return render_template('show_titles.html', titles=titles)

@app.route('/synced')
def show_synced():
    titles = (Comic
              .select()
              .where(Comic.scraped == True)
              .order_by(Comic.title)
              .dicts())
    return render_template('show_titles.html', titles=titles, synced=True)

@app.route('/search')
def show_search():
    tcount = Comic.select().count()
    icount = Issue.select().count()
    if request.query_string:
        search = request.args.get('q')
        advanced = request.args.get('adv')
        if advanced == 'on':
            start = process_time()
            query = (Comic
                     .select()
                     .where(Comic.search_title.match(search))
                     .order_by(Comic.scraped.desc(), Comic.title)
                     .dicts())
            elapsed = process_time() - start
        else:
            start = process_time()
            query = (Comic
                     .select()
                     .where(Expression(Comic.search_title, 'T@@', fn.plainto_tsquery(search)))
                     .order_by(Comic.scraped.desc(), Comic.title)
                     .dicts())
            elapsed = process_time() - start
        return render_template('show_search.html',
                               totals=(tcount, icount),
                               results=query,
                               search=True,
                               query=search,
                               adv=advanced,
                               elapsed=round(elapsed*1000, 4))

    return render_template('show_search.html', totals=(tcount, icount))

@app.route('/title/<int:title_id>')
def title_by_id(title_id):
    title = Comic.get(Comic.id == title_id)
    query = (Issue
             .select(Issue, Comic)
             .join(Comic)
             .order_by(Issue.num)
             .where(Issue.series == title_id))
    issues = [model_to_dict(row) for row in query]
    return render_template('show_titles_id.html', title=model_to_dict(title), issues=issues)


@app.route('/refresh/titles')
def refresh_titles():
    titles = q.enqueue(import_titles)
    flash('Scraping titles has been queued, please refresh in a few seconds')
    return redirect(url_for('show_titles'))

@app.route('/refresh/issues/<int:title_id>')
def refresh_issues(title_id):
    comic = Comic.get(Comic.id == title_id)
    Issue.delete().where(Issue.series == title_id).execute()
    issues = q.enqueue(import_issues, title_id)
    flash('Scraping issues for {} has been queued, please refresh in a few seconds'.format(comic.title))
    return redirect(url_for('title_by_id', title_id=title_id))

if __name__ == "__main__":
    app.run(debug=True)
