import datetime as dt

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template

from monolith.auth import current_user
from monolith.database import Story, db


home = Blueprint('home', __name__)


@home.route('/')
def index():
    stats = {}
    message = ''

    if current_user is not None and hasattr(current_user, 'id'):
        stories = Story.query.filter_by(author_id=current_user.id) \
                             .order_by(Story.date.desc()).all()

        # If I have at least one story, I can start collecting statistics
        if stories:
            # Querying stories statistics, such as total number of stories,
            # number of likes, dislikes
            stories_stats = db.session.query(
                db.func.count(Story.likes).label('number_of_stories'),
                db.func.sum(Story.likes).label('total_likes'),
                db.func.sum(Story.dislikes).label('total_dislikes')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id).first()

            stats['stories'] = stories_stats

            # Stats related to dice
            n_dice = [len(story.dice_set) for story in stories]
            avg_dice = round(sum(n_dice) / len(n_dice), 2)

            stats['avg_dice'] = avg_dice

            # Computing the post frequency
            # Number of days from the first story to today
            n_days = (dt.datetime.now() - stories[-1].date).days + 1
            n_stories = stories_stats.number_of_stories
            stats['stories_frequency'] = n_stories / n_days

            # Checking if the user is an active one
            # (i.e. He posts at least one story in the last seven days)
            delta = dt.datetime.now() - dt.timedelta(days=7)
            stats['active'] = True if delta < stories[0].date else False
    else:
        stories = None
        message = 'login needed'

    return render_template('index.html', stories=stories, stats=stats, message=message)
