from flask import Blueprint, abort
from flask import current_app as app
from flask import jsonify, redirect, render_template, request

from flask_login import current_user, login_required, login_user

from monolith.database import Story, User, db
from monolith.forms import UserForm

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

users = Blueprint('users', __name__)


@users.route('/users')
@login_required
def users_():
    res = db.session.query(User.username, Story.text, func.max(Story.date)) \
            .outerjoin(Story).group_by(User.id).all()
    return render_template('users.html', result=res)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserForm()
    status = 200
    if form.validate_on_submit():
        new_user = User()
        form.populate_obj(new_user)
        new_user.set_password(form.password.data)
        db.session.add(new_user)

        try:
            db.session.commit()
            login_user(new_user)
            return redirect('/')
        except IntegrityError as e:
            status = 409
            if 'user.username' in str(e):
                err = 'This username already exists.'
            elif 'user.email' in str(e):
                err = 'This email is already used.'

            if app.config['TESTING']:
                return jsonify(error=err), status
            form.email.errors.append(err)

    return render_template('signup.html', form=form), status


@users.route('/users/<user_id>/follow', methods=['DELETE', 'POST'])
@login_required
def follow(user_id):
    """
    POST requests add the user with primary key `user_id` to the list of
    user followed by the currenly logged user. If it is already in the list
    returns successfully without updating the database.
    DELETE requests remove the user from the list and if it is not in the list
    returns successfully without updating the database.
    User must be logged to access this endpoint.
    All responses are in JSON format and are meant to be invokated within the
    the frontend (eg. AJAX or fetch), not by url access.
    """

    followee = User.query.get(user_id)
    if followee is None:
        message = 'User with id {} does not exist'.format(user_id)
        return (jsonify(error=message), 404)

    if followee == current_user:
        return (jsonify(error='Cannot follow or unfollow yourself'), 400)

    if request.method == 'POST':
        current_user.follows.append(followee)
        db.session.commit()
        return jsonify(message='User followed')

    if request.method == 'DELETE':
        try:
            current_user.follows.remove(followee)
            db.session.commit()
        except ValueError:
            pass
        return jsonify(message='User unfollowed')

    abort(405)


def _get_followed_dict(user_id):
    me = User.query.get(user_id)
    users = [{'firstname': x.firstname, 'lastname': x.lastname, 'id': x.id}
             for x in me.follows]
    return {'users': users}


@users.route('/followed', methods=['GET'])
@login_required
def get_followed():
    template_dict = _get_followed_dict(current_user.id)
    return render_template('followed.html', **template_dict)
