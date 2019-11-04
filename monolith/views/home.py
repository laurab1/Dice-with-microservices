from flask import Blueprint, render_template, jsonify
from flask import current_app as app

from monolith.auth import current_user
from monolith.database import Story, db


home = Blueprint('home', __name__)

@home.route('/')
def index():
    stats = {}
    if current_user is not None and hasattr(current_user, 'id'):
        stories = db.session.query(Story).filter(
            Story.author_id == current_user.id).all()
            

        likes = db.session.query(
                db.func.sum(Story.likes).label('total'),
                db.func.count(Story.likes).label('number_of_stories'),
                db.func.sum(Story.dislikes).label('total_dislikes')
            ).filter(
                Story.author_id == current_user.id
            ).group_by(Story.author_id).all()

        stats['likes'] = likes[0]
        
        print(stats['likes'].total)
        if stories != []:
            n_dice = [len(story.dice_set.split('?')) for story in stories]
            avg_dice = round(sum(n_dice) / len(n_dice), 2)
        
        stats['avg_dice'] = avg_dice

        if app.config['TESTING']:
            return jsonify({'stories':[s.toJSON() for s in stories]})
    else:
        stories = None
        if app.config['TESTING']:
            return jsonify(login='needed')

    return render_template('index.html', stories=stories, stats=stats)
