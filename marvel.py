# all THE IMPORTS!
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from scrape import *
from contextlib import closing

# configuration
DATABASE = '/tmp/marvel.db'
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
        return plural

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_front():
    return render_template('frontpage.html')

@app.route('/titles')
def show_titles():
    cur = g.db.execute('select title, id, startyear, endyear, scraped from titles')
    titles = [dict(title=row[0], id=row[1], startyear=row[2], endyear=row[3], scraped=row[4]) for row in cur.fetchall()]
    return render_template('show_titles.html', titles=titles)

@app.route('/synced')
def show_synced():
    cur = g.db.execute('select title, id, startyear, endyear, scraped from titles where scraped = 1')
    titles = [dict(title=row[0], id=row[1], startyear=row[2], endyear=row[3], scraped=row[4]) for row in cur.fetchall()]
    return render_template('show_titles.html', titles=titles)

@app.route('/search')
def show_search():
    tcur = g.db.execute('select count(*) from titles').fetchall()[0][0]
    icur = g.db.execute('select count(*) from issues').fetchall()[0][0]
    if request.query_string:
        query = request.args.get('q')
        cur = g.db.execute('select title, id, startyear, endyear, scraped from titlesearch where titlesearch match ?', [query])
        print(cur)
        results = [dict(title=row[0], id=row[1], start=row[2], end=row[3], scraped=row[4]) for row in cur.fetchall()]
        return render_template('show_search.html', totals=(tcur, icur), results=results)

    return render_template('show_search.html', totals=(tcur, icur), results=())

@app.route('/title/<int:title_id>')
def title_by_id(title_id):
    tcur = g.db.execute('select title, startyear, endyear from titles where id = ?', [title_id]).fetchall()[0]
    title = dict(title=tcur[0], id=title_id, startyear=tcur[1], endyear=tcur[2])
    icur = g.db.execute('select title, id, link from issues where series = ?', [title_id])
    issues = [dict(title=row[0], id=row[1], link=row[2]) for row in icur.fetchall()]
    return render_template('show_titles_id.html', title=title, issues=issues)

@app.route('/refresh/titles')
def refresh_titles():
    g.db.execute('delete from titles')
    titles = scrape_titles()
    for title in titles:
        if type(title[1]) is tuple:
            g.db.execute('insert into titles (title, id, startyear, endyear) values (?, ?, ?, ?)',
                         [title[0], title[2], title[1][0], title[1][1]])
            g.db.execute('insert into titlesearch (title, id, startyear, endyear) values (?, ?, ?, ?)',
                         [title[0], title[2], title[1][0], title[1][1]])
        else:
            g.db.execute('insert into titles (title, id, startyear) values (?, ?, ?)',
                         [title[0], title[2], title[1]])
            g.db.execute('insert into titlesearch (title, id, startyear) values (?, ?, ?)',
                         [title[0], title[2], title[1]])
    g.db.commit()
    return redirect(url_for('show_titles'))

@app.route('/refresh/issues/<int:title_id>')
def refresh_issues(title_id):
    title = g.db.execute('select title, id, startyear, endyear from titles where id = ?', [title_id]).fetchall()[0]
    g.db.execute('delete from issues where series = ?', [title[1]])
    data = coerce_to_data(title)
    issues = scrape_issues(data)
    for issue in issues:
        g.db.execute('insert into issues (title, id, link, series) values (?, ?, ?, ?)',
                     [issue[0], issue[2], issue[1], title[1]])
    g.db.execute('update titles set scraped = 1 where id = ?', [title_id])
    g.db.execute('update titlesearch set scraped = 1 where id = ?', [title_id])
    g.db.commit()
    return redirect(url_for('title_by_id', title_id=title[1]))

if __name__ == "__main__":
    app.run()
