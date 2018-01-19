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



class ResetPasswordForm(Form):
    email = StringField('Please Enter your Email address', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('RESET PASSWORD')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Email not registered. Please register!')

class ConfirmPasswordForm(Form):
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password2', message='Passwords '
                                                                                               'must match.')])
    submit = SubmitField('Reset')