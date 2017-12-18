from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    link = db.Column(db.String(200), unique=True, index=True)
    word_assoc = db.relationship('PageWord', backref=db.backref("page"), cascade="all, delete-orphan",
                                 single_parent=True, lazy='dynamic')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link
        }


class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, index=True)
    page_assoc = db.relationship('PageWord', backref=db.backref("word"), cascade="all, delete-orphan",
                                 single_parent=True, lazy='dynamic')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class PageWord(db.Model):
    __tablename__ = 'page_word'
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    count = db.Column(db.Integer, default=0)
