# -*- coding: utf-8 -*-
import re
import string
import urllib2

from flask import Flask, jsonify, request
from flask.helpers import send_file
from flask.templating import render_template
from lxml import html

from models import db, Page, Word, PageWord

# App config
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.url_map.strict_slashes = False
db.app = app
db.init_app(app)

# Globals
DIRTY_EXTENSIONS = ['png', 'jpg', 'gif', 'jpeg']
SKIP_LINKS = ['#', '/']


@app.route('/', methods=('GET',))
def index():
    # page1 = Page(title="First Page", link="http://www.page1.com")
    # # page2 = Page(title="Second Page", link="http://www.page2.com")
    #
    # word1 = Word(name="biscuit")
    # word2 = Word(name="creamy")
    # word3 = Word(name="chocolate")
    #
    # occurrence1 = PageWord(page=page1, word=word1, count=20)
    # occurrence2 = PageWord(page=page1, word=word2, count=10)
    # occurrence3 = PageWord(page=page1, word=word3, count=30)
    #
    # db.session.add_all([occurrence1, occurrence2, occurrence3])
    #
    # db.session.commit()

    return render_template('index.html')


@app.route('/partials/<path:template>')
def send_template(template):
    return send_file('templates/partials/{}'.format(template))


@app.route('/index')
def index_url():
    origin = 'http://localhost:1337'
    nlc, nwc = process_url(origin, set([origin]))
    return 'ok'


@app.route('/search', methods=('GET',))
def search():
    word = request.args.get('word', '', type=str)
    return search_word(word)


def search_word(word):
    word_obj = Word.query.filter_by(name=word).first()
    occurrences = PageWord.query.filter_by(word=word_obj).order_by('count asc').all()
    return jsonify(result=[o.serialize for o in occurrences])


def index_html(html_text, origin, title):
    nwc = nlc = 0
    first_clean = re.sub(r'<(style|script)[\s]+[type="text/javascript"]*[>]+.*(</(style|script)>)+', '', html_text)
    full_clean_data = re.sub('[{}\d]'.format(re.escape(string.punctuation)), ' ', re.sub(r'<[^>]+>', '', first_clean))

    page_data = {'origin': origin, 'title': title, 'words': []}
    words = full_clean_data.split()
    counted = []
    occurrences = []
    page = Page.query.filter_by(link=origin).first()
    if not page:
        nlc += 1
        page = Page(title=title, link=origin)
    for w in words:
        if w not in counted:
            count = words.count(w)
            page_data['words'].append((w, count))
            counted.append(w)
            word = Word.query.filter_by(name=w.decode('utf-8')).first()
            if not word:
                nwc += 1
                word = Word(name=w.decode('utf-8'))
            occurrence = PageWord.get(page=page, word=word)
            if not occurrence:
                occurrence = PageWord.get(page=page, word=word, count=count)
            else:
                occurrence.count = count
            occurrences.append(occurrence)
            print '{0}: there are {1} of word {2}'.format(origin, count, w)
    db.session.add_all(occurrences)
    db.session.commit()
    return nwc, nlc


def is_safe(link):
    _is_safe = True
    if link in SKIP_LINKS:
        _is_safe = False
    elif ('.' in link.split('/')[-1] and link.split('/')[-1].split('.')[-1] or '') in DIRTY_EXTENSIONS:
        _is_safe = False
    return _is_safe


def process_url(origin, verified_links, depth=2):
    try:
        page = urllib2.urlopen(origin)
        html_src = page.read()
        page.close()
        parsed_html = html.fromstring(html_src)
    except Exception, ex:
        return
    title = parsed_html.xpath('//head/title/text()') and parsed_html.xpath('head//title/text()')[0] or 'Untitled Page'
    index_html(html_src, origin, title)
    new_links = set()
    for link in parsed_html.xpath('//a/@href'):
        if is_safe(link) and link not in verified_links:
            valid_link = link
            if 'http' not in link:
                protocol, address = origin.split('//')
                domain = address.split('/')[0]
                valid_link = '%s//%s%s' % (protocol, domain, not link.startswith('/') and '/' + link or link)
            if valid_link not in verified_links:
                new_links.add(valid_link)
    if depth > 0:
        verified_links.update(verified_links.union(new_links))
        for l in new_links:
            print 'depth: %s' % str(depth)
            process_url(l, verified_links, depth=depth - 1)
    return verified_links


if __name__ == '__main__':
    db.create_all()
    app.run()
