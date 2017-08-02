from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField, DateTimeField, FileField, SelectFieldBase
from wtforms.validators import  Length, DataRequired, Email, Regexp, ValidationError, Optional

from ..models import Role, User, Event, Ticket

class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(10, 14)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),Email()])
    username = StringField('Username', validators=[
    DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    account_balance = IntegerField('Account Balance')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


    def validate_phone_number(self, field):
        if field.data != self.user.phone_number and \
                User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use.')


class CreateEventForm(Form):
    title = StringField('Event title', validators=[Length(1, 64), DataRequired()])
    logo = FileField("Choose an event logo")
    description =  TextAreaField('Event description', validators=[Length(0, 100), Optional()])
    location = StringField('Event Location', validators=[Length(0, 64), DataRequired()])
    date = DateTimeField("Event Date",format="%d/%m/%Y %H:%M",validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateTicketForm(Form):
    type = SelectField('Ticket Type', coerce=int)
    price = StringField('Price of Ticket', validators=[DataRequired()])
    count = IntegerField("Number of Tickets Available", validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_price(self, field):
        try:
            int(field.data)
        except:
            raise ValidationError("Price must be a valid integer.")

