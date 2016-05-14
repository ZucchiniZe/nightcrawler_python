# -*- coding: utf-8 -*-

# ALL THE IMPORTS!
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from scrape import *
from db import *
from playhouse.shortcuts import model_to_dict
from contextlib import closing

# configuration
DATABASE = '/tmp/marvel.db'
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)


def init_db():
    db.connect()
    db.create_tables([Comic, Issue, ComicSearch])
    db.close()

def coerce_to_data(cur):
    return (cur[0], (cur[2], cur[3]), cur[1])

@app.template_filter('scraped')
def bool_filter(i):
    scraped = bool(i)
    if scraped:
        return "✓"
    else:
        return "✗"

@app.template_filter('pluralize')
def pluralize(number, singular = '', plural = 's'):
    if number == 1:
        return singular
    else:
        return plural\

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

@app.route('/')
def show_front():
    return render_template('frontpage.html')

@app.route('/titles')
def show_titles():
    titles = [model_to_dict(row) for row in Comic.select()]
    return render_template('show_titles.html', titles=titles)

@app.route('/synced')
def show_synced():
    titles = [model_to_dict(row) for row in Comic.select().where(Comic.scraped == True)]
    return render_template('show_titles.html', titles=titles, synced=True)

@app.route('/search')
def show_search():
    tcount = Comic.select().count()
    icount = Issue.select().count()
    if request.query_string:
        search = request.args.get('q')
        query = (ComicSearch
                 .select(Comic)
                 .join(Comic, on=ComicSearch.comic_id == Comic.id)
                 .where(ComicSearch.match(search))
                 .dicts())
        return render_template('show_search.html', totals=(tcount, icount), results=query)

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

def remove_cruft(titles):
    del titles['start'], titles['end'], titles['scraped']
    titles['comic_id'] = titles.pop('id')
    return titles

@app.route('/refresh/titles')
def refresh_titles():
    titles = scrape_titles()
    with db.atomic():
        for idx in range(0, len(titles), 199):
            Comic.insert_many(titles[idx:idx+199]).upsert().execute()
    stitles = list(map(remove_cruft, titles))
    with db.atomic():
        for idx in range(0, len(titles), 199):
            ComicSearch.insert_many(stitles[idx:idx+199]).upsert().execute()
    return redirect(url_for('show_titles'))

@app.route('/refresh/issues/<int:title_id>')
def refresh_issues(title_id):
    comic = Comic.get(Comic.id == title_id)
    issues = scrape_issues(model_to_dict(comic))
    issues = list(map(lambda x: dict({'series': comic}, **x), issues))
    print(issues)
    with db.atomic():
        for idx in range(0, len(issues), 199):
            Issue.insert_many(issues[idx:idx+199]).upsert().execute()
    Comic.update(scraped=True).where(Comic.id == title_id).execute()
    return redirect(url_for('title_by_id', title_id=title_id))

if __name__ == "__main__":
    app.run()
