from flask import Blueprint, Response, redirect, render_template, url_for

from flask_login import current_user, login_user, logout_user

from monolith.database import User
from monolith.forms import LoginForm


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Performs the login of a user. 
    It checks whether the input is the username or the e-mail address, 
    the password and performs the authentication.

    Returns:
        302 -> redirection to the user's homepage if the authentication is succesful
        200 -> the login page with the corresponding error message
    '''
    form = LoginForm()
    form.password.errors = []

    if form.validate_on_submit():
        cred, password = form.data['usrn_eml'], form.data['password']

        if '@' in cred:
            user = User.query.filter_by(email=cred).one_or_none()
        else:
            user = User.query.filter_by(username=cred).one_or_none()

        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect(url_for('home.index'))

        form.password.errors.append('Wrong username or password.')

    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    '''
    Performs the logout of the user.

    Returns:
        302 -> redirection to the welcome page if a user was logged in
        203 -> notifies that the operation was not needed
    '''
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home.index'))

    return Response(status=203)
