from flask import Blueprint, Response, redirect, render_template, url_for

from flask_login import current_user, login_user, logout_user

from monolith.database import User, db
from monolith.forms import LoginForm


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.password.errors = []

    if form.validate_on_submit():
        cred, password = form.data['usrn_eml'], form.data['password']
        if '@' in cred:
            user = db.session.query(User).filter(User.email == cred).first()
        else:
            user = db.session.query(User).filter(User.username == cred).first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect(url_for('home.index'))
        form.password.errors.append('Wrong username or password.')
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home.index'))
    return Response(status=203)
