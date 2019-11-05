from flask_login import LoginManager, current_user

from monolith.database import User


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user
