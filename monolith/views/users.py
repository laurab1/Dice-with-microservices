from flask import Blueprint, redirect, render_template, request, jsonify
from monolith.database import db, User
from monolith.auth import admin_required
from monolith.forms import UserForm
from sqlalchemy.exc import IntegrityError
from os import urandom


users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User()
        form.populate_obj(new_user)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect('/users')
        except IntegrityError as e:
            if 'user.username' in str(e):
                return jsonify({'Error': 'This username already exists.'})
            elif 'user.email' in str(e):
                return jsonify({'Error': 'This email address is already used.'})
        
    return render_template('signup.html', form=form)
