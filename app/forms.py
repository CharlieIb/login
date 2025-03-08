# from operator import contains
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField, IntegerField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, NumberRange, EqualTo, Length, ValidationError
import re


def contains(digit=-1, upper=-1, lower=-1, special=-1):

    def _contains(form, field):
        freq = {'digit': 0, 'upper': 0, 'lower': 0, 'special': 0}

        special_characters = set("!@#$%^&*()_+-=[]{};':\",./<>?`~")

        for i in field.data:
            if i.isdigit():
                freq['digit'] += 1
            elif i.isupper():
                freq['upper'] += 1
            elif i.islower():
                freq['lower'] += 1
            elif i in special_characters:
                freq['special'] += 1
        if (digit == -1 or freq['digit'] >= digit and
                upper == -1 or freq['upper'] >= upper and
                lower == -1 or freq['lower'] >= lower and
                special == -1 or freq['special'] >= special):
            return True
        else:
            raise ValidationError(
                'Password must contain at least: '
                f'{digit} digit(s), {upper} uppercase letter(s), '
                f'{lower} lowercase letter(s), and {special} special character(s).'
            )
    return _contains



class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(),
                                                         Length(min=8),
                                                         EqualTo('password2'),
                                                         contains(digit=1, upper=1, lower=1, special=1)])
    password2 = PasswordField('Re-enter new Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=8),
                                                     EqualTo('password2'),
                                                     contains(digit=1, upper=1, lower=1, special=1)])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    role = SelectField('Role', choices=['normal','admin'], default='normal', validators=[DataRequired()])
    submit = SubmitField('Register')

class SubmitForm(FlaskForm):
    choose = HiddenField('Choice')
    toggle = SubmitField()

