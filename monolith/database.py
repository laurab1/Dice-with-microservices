import datetime as dt
import json
from random import randint

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.hybrid import hybrid_property

from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


"""Followers table, provides the many-to-many relationship between followers
and followee. Primary key is composed by both the foreign keys."""
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'),
              primary_key=True),
    db.Column('followee_id', db.Integer, db.ForeignKey('user.id'),
              primary_key=True)
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Unicode(128), unique=True, nullable=False)
    email = db.Column(db.Unicode(128), unique=True, nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    tel_id = db.Column(db.Unicode(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False

    # All operations on the relationship can be done via the this property that
    # lazily exposes the list of followed users or the followed property that
    # provides the list of followees.
    follows = db.relationship('User', secondary=followers,
                              primaryjoin=id == followers.c.follower_id,
                              secondaryjoin=id == followers.c.followee_id,
                              lazy='subquery',
                              backref=db.backref('followed', lazy=True))

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        salt = randint(16, 32)
        self.password = generate_password_hash(password, salt_length=salt)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Story(db.Model):
    __tablename__ = 'story'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text(1000))  # around 200 (English) words
    date = db.Column(db.DateTime)
    is_draft = db.Column(db.Boolean, nullable=False, default=True)

    # will store the number of likes, periodically updated in background
    likes = db.Column(db.Integer)
    # will store the number of dislikes
    dislikes = db.Column(db.Integer)

    theme = db.Column(db.Text(64))
    _dice_set = db.Column(db.Text(100), nullable=False)

    deleted = db.Column(db.Boolean, default=False)
    # define foreign key
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', foreign_keys='Story.author_id')

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.date = dt.datetime.now()

    @hybrid_property
    def dice_set(self):
        return json.loads(self._dice_set)

    @dice_set.setter
    def dice_set(self, dice_set):
        self._dice_set = json.dumps(dice_set)


class Reaction(db.Model):
    __tablename__ = 'reaction'
    reactor_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                           primary_key=True)
    reactor = db.relationship('User', foreign_keys='Reaction.reactor_id')

    story_id = db.Column(db.Integer, db.ForeignKey('story.id'),
                         primary_key=True)
    author = db.relationship('Story', foreign_keys='Reaction.story_id')

    reaction_val = db.Column(db.Integer)

    # True iff it has been counted in Story.likes
    marked = db.Column(db.Boolean, default=False)
