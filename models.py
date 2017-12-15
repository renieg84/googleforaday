from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    link = db.Column(db.String, unique=True, index=True)


class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)


class PageWord(db.Model):
    __tablename__ = 'page_word'
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    count = db.Column(db.Integer, default=0)
    page = db.relationship(Page, backref=db.backref("word_assoc"))
    word = db.relationship(Word, backref=db.backref("page_assoc"))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'word': self.word.name,
            'page': {'title': self.page.title, 'link': self.page.link},
            'count': self.count
        }
