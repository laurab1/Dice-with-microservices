from flask_wtf import FlaskForm
import wtforms as f
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional


class LoginForm(FlaskForm):
    usrn_eml = f.StringField('E-mail or username', id='usrn_eml', validators=[DataRequired()])
    password = f.PasswordField('Password', id='password', validators=[DataRequired()])
    display = ['usrn_eml', 'password']


class UserForm(FlaskForm):
    email = EmailField('E-mail*', id='email', validators=[DataRequired(), Email()])
    username = f.StringField('Username*', 
                            id='username', 
                            validators=[DataRequired(),
                                        Regexp('^\w+$', message="Username must contain only letters, numbers or underscore."),
                                        Length(min=5, max=25, message="Username must be betwen 5 and 25 characters")])
    password = f.PasswordField('Password*', id='password', validators=[DataRequired(), Length(min=8, max=64)])
    firstname = f.StringField('First Name', id='firstname', validators=[Length(max=64), Optional()])
    lastname = f.StringField('Last Name', id='lastname', validators=[Length(max=64), Optional()])
    dateofbirth = DateField('Date of Birth', id='dateofbirth', validators=[Optional()])
    display = ['email', 'username', 'password','firstname', 'lastname', 'dateofbirth']


class StoryForm(FlaskForm):
    diceset = ""
    text = f.TextField('text', validators=[DataRequired(), Length(max=1000)])
    display = ['text']
