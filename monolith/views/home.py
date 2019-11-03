from flask import Blueprint, render_template
from flask import current_app as app

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
                db.func.sum(Story.likes).label('total'),
                db.func.count(Story.likes).label('number_of_stories')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id)

        dislikes = db.session.query(
                db.func.sum(Story.dislikes).label('total')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id)

    else:
        stories = None
        likes = None

    if app.config["TESTING"] == True:
        app.config["TEMPLATE_CONTEXT"] = jsonify({'stories': str(stories), 'likes': str(likes), 'dislikes': str(dislikes)})

    return render_template("index.html", stories=stories, likes=likes, dislikes=dislikes)
