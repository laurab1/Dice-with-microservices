from flask import Blueprint, render_template

from monolith.auth import current_user
from monolith.database import Story, db


home = Blueprint('home', __name__)


def _strava_auth_url(config):
    return '127.0.0.1:5000'


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        stories = db.session.query(Story).filter(
            Story.author_id == current_user.id)

        likes = db.session.query(
                db.func.sum(Story.likes).label('total')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id)

    else:
        stories = None
        likes = None

    return render_template("index.html", stories=stories, likes=likes)
