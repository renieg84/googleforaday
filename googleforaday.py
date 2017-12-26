# -*- coding: utf-8 -*-
import re
import string
import urllib2

from flask import Flask, jsonify, request
from flask.helpers import send_file
from flask.templating import render_template
from lxml import html
from lxml.html import HtmlElement

from models import db, Page, Word, PageWord

# App config
app = Flask(__name__)
app.config['DEBUG'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/googleforaday'
# app.url_map.strict_slashes = False
db.app = app
db.init_app(app)

# Globals
SKIP_LINKS = ['#', '/']
SKIP_TAGS = ['script', 'style']


@app.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@app.route('/partials/<path:template>')
def send_template(template):
    return send_file('templates/partials/{}'.format(template))


@app.route('/index-url', methods=('POST', 'PUT',))
def index_url():
    origin = request.args.get('url', '', type=str)
    if not origin:
        return jsonify('empty')
    nw, nl = process_url(origin, set([origin]))
    return jsonify({'nw': nw, 'nl': nl})


@app.route('/clear-index', methods=('POST',))
def clear_index():
    try:
        db.session.query(PageWord).delete()
        db.session.query(Page).delete()
        db.session.query(Word).delete()
        db.session.commit()
    except Exception, ex:
        db.session.rollback()
    return jsonify({'cleaned': True})


@app.route('/search-word', methods=('GET',))
def search():
    try:
        word = request.args.get('word', '')
        result = search_word(word.encode('UTF-8'))
    except Exception, ex:
        result = []
    return result


def search_word(word):
    w = db.session.query(Word).filter(Word.name.ilike('%{0}%'.format(word))).first()
    result = []
    if w:
        occurrences = w.page_assoc.order_by('count desc').all()
        for o in occurrences:
            result.append({
                'count': o.count,
                'word': o.word.name,
                'page': {'link': o.page.link, 'title': o.page.title}})
    return jsonify(result=result)


def count_word(a, elems):
    count = 0
    for elem in elems:
        try:
            if elem.lower() == a:
                count += 1
        except Exception, ex:
            continue
    return count


def get_text(element, result=[]):
    if element.text and element.text.strip():
        result.append(element.text.strip())
    if element.tail and element.tail.strip():
        result.append(element.tail.strip())
    children = element.getchildren()
    if children:
        for elem in filter(lambda e: isinstance(e, HtmlElement) and e.tag not in SKIP_TAGS, children):
            get_text(elem)

    return " ".join(result)


def index_html(parsed_html, origin, title):
    body_text = get_text(parsed_html)
    nwc = nlc = 0
    full_clean_data = re.sub(r'[{0}\d]'.format(re.escape(string.punctuation)), ' ', body_text)
    words = []
    for line in full_clean_data.splitlines():
        words.extend(line.split())
    counted = []
    occurrences = []
    page = Page.query.filter_by(link=origin).first()
    if not page:
        nlc += 1
        page = Page(title=title, link=origin)
        db.session.add(page)
    for w in words:
        try:
            lower_word = w.lower()
            if lower_word not in counted:
                count = count_word(lower_word, [e for e in words if e not in counted])
                counted.append(lower_word)
                word = Word.query.filter_by(name=lower_word).first()
                if not word:
                    nwc += 1
                    word = Word(name=lower_word)
                    db.session.add(word)
                occurrence = PageWord.query.filter_by(page=page, word=word).first()
                if not occurrence:
                    occurrence = PageWord(page=page, word=word, count=count)
                    occurrences.append(occurrence)
                elif occurrence.count != count:
                    occurrence.count = count
                    occurrences.append(occurrence)
        except Exception, ex:
            continue
    try:
        db.session.add_all(occurrences)
        db.session.commit()
    except Exception, ex:
        db.session.rollback()
        return 0, 0
    return nwc, nlc


def is_safe(link):
    return link not in SKIP_LINKS


def process_url(origin, links=None, nw=0, nl=0, depth=2):
    try:
        page = urllib2.urlopen(origin)
        html_src = page.read()
        page.close()
        parsed_html = html.fromstring(html_src)
    except Exception, ex:
        return nw, nl
    print 'Scrapping site: {0} with depth={1}'.format(origin, depth)
    title = parsed_html.xpath('//head/title/text()') and parsed_html.xpath('head//title/text()')[0] or 'Untitled Page'
    _nw, _nl = index_html(parsed_html.xpath('//body')[0], origin, title)
    nw += _nw
    nl += _nl
    links.add(origin)
    new_links = set()
    for link in parsed_html.xpath('//a/@href'):
        if is_safe(link):
            if 'http' not in link:
                protocol, address = origin.split('//')
                domain = address.split('/')[0]
                valid_link = '%s//%s%s' % (protocol, domain, not link.startswith('/') and '/' + link or link)
                new_links.add(valid_link)
    if depth > 0:
        for l in new_links.difference(links):
            nw, nl = process_url(l, links=links, nw=nw, nl=nl, depth=depth - 1)
    return nw, nl


if __name__ == '__main__':
    db.create_all()
    app.run()
