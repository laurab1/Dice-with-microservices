from flask import Blueprint, render_template, jsonify
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
            Story.author_id == current_user.id).all()

        likes = db.session.query(
                db.func.sum(Story.likes).label('total'),
                db.func.count(Story.likes).label('number_of_stories')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id)

        if app.config['TESTING']:
            return jsonify({'stories':[s.toJSON() for s in stories]})
    else:
        stories = None
        if app.config['TESTING']:
            return jsonify(login='needed')

    return render_template('index.html', stories=stories, likes=likes)
