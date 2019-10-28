from flask import Blueprint, render_template, redirect, request, jsonify, Response
from flask_login import (current_user, login_user, logout_user,
                         login_required)

from monolith.database import db, User
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.password.errors = []
    if form.validate_on_submit():
        cred, password = form.data['usrn_eml'], form.data['password']
        if '@' in cred:
            q = db.session.query(User).filter(User.email == cred)
        else:
            q = db.session.query(User).filter(User.username == cred)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect('/')
        else:
            return jsonify({'Error': 'Wrong username or password.'})
    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return Response(status=203)
