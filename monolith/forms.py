from flask_wtf import FlaskForm
import wtforms as f
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = EmailField('E-mail address*', id='email', validators=[DataRequired(), Email()])
    username = f.StringField('Username*', id='username', validators=[DataRequired()])
    password = f.PasswordField('Password*', id='password', validators=[DataRequired(), Length(min=8, max=64)])
    firstname = f.StringField('First Name*', id='firstname', validators=[DataRequired()])
    lastname = f.StringField('Last Name*', id='lastname', validators=[DataRequired()])
    dateofbirth = DateField('Date of Birth', id='dateofbirth', format="%Y-%m-%d")
    display = ['email', 'username', 'password','firstname', 'lastname', 'dateofbirth']

class StoryForm(FlaskForm):
    text = f.TextField('text', validators=[DataRequired()]) #TODO: Add check on length (1000 chrs)
    display = ['text']