from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp, EqualTo

from app.model import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("Email not registered")


class RegistrationForm(Form):
    phone_number = StringField("Phone number", validators=[DataRequired(), Length(13)])
    email = StringField('Email', validators=[Optional(), Length(1, 64),
    Email()])
    city = StringField('City', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    'Usernames must have only letters, '
    'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    confirm = BooleanField('I agree to terms and conditions')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if field.data:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_phone_number(self, field):
        phone_number = field.data
        if not phone_number.startswith("+"):
            raise ValidationError('Invalid phone number. Phone number should start with country code.')
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use.')
