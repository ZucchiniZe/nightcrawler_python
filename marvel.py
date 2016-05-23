# -*- coding: utf-8 -*-

# ALL THE IMPORTS!
import analytics
import uuid
import datetime
from flask import Flask, request, g, redirect, url_for, render_template, flash
from celery import Celery
from time import process_time
from playhouse.shortcuts import model_to_dict
from opbeat.contrib.flask import Opbeat
from scrape import *
from db import *

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)

app.secret_key = 'sekrit'

redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
app.config.update(
    CELERY_BROKER_URL=redis_url,
    CELERY_RESULT_BACKEND=redis_url,
)

celery = make_celery(app)

opbeat = Opbeat(
    app,
    organization_id='e4a92e8bae9a4cd9b82ad1ccb4f09f83',
    app_id='10c2a61210',
    secret_token='fb88ac5a782f33e09260b785b650cfff98df5c1f',
)

analytics.write_key = '3jPlLTLsajh0UoIfYq3L95EdiErVaZ57'

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

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@celery.task(name='scrape_issues')
def import_issues(title_id):
    Issue.delete().where(Issue.series == title_id).execute()
    comic = Comic.get(Comic.id == title_id)
    analytics.track(str(uuid.uuid4()), 'Refresh Issues', {
        'series': comic.title,
        'timestamp': datetime.datetime.now()
    })
    issues = scrape_issues(model_to_dict(comic))
    issues = list(map(lambda x: dict({'series': comic}, **x), issues))

    with db.atomic():
        for idx in range(0, len(issues), 199):
            Issue.insert_many(issues[idx:idx+199]).execute()
            Comic.update(scraped=True).where(Comic.id == title_id).execute()

@celery.task(name='scrape_titles')
def import_titles():
    analytics.track(str(uuid.uuid4()), 'Refresh Titles', {
        'timestamp': datetime.datetime.now()
    })
    Comic.delete().execute()
    titles = scrape_titles()
    titles = list(map(lambda x: dict({'search_title': fn.to_tsvector(x['title'])}, **x), titles))

    with db.atomic():
        for idx in range(0, len(titles), 150):
            Comic.insert_many(titles[idx:idx+150]).execute()


@app.route('/')
def show_front():
    return render_template('frontpage.html')

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
    titles = import_titles.delay()
    flash('Scraping titles has been queued, please refresh in a few seconds')
    return redirect(url_for('show_titles'))

@app.route('/refresh/issues/<int:title_id>')
def refresh_issues(title_id):
    comic = Comic.get(Comic.id == title_id)
    issues = import_issues.delay(title_id)
    flash('Scraping issues for {} has been queued, please refresh in a few seconds'.format(comic.title))
    return redirect(url_for('title_by_id', title_id=title_id))

if __name__ == "__main__":
    app.run(debug=True)
