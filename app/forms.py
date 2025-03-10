# from operator import contains
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField, IntegerField, SelectField
# from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, NumberRange, EqualTo, Length, ValidationError, Optional
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



class NotEqualTo(object):
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data == other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext('Field must be equal to %(other_name)s.')

            raise ValidationError(message % d)



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
    email = StringField('Primary email', validators=[DataRequired()])
    backup_email = StringField('Secondary email(Optional)', validators=[NotEqualTo('email')])
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




class EmailChange(FlaskForm):
    choose = SelectField('Primary or Secondary Email', choices=[('0','Primary'),('1','Secondary')], default=('0','Primary'), validators=[DataRequired()])
    oldEmail = StringField('Old email (leave blank if none)')
    email = StringField('New Email', validators=[DataRequired(), EqualTo('email2')])
    email2 = StringField('Re-enter Email', validators=[DataRequired()] )
    submit = SubmitField('Update Email')


