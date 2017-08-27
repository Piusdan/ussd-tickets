from flask_wtf import FlaskForm as Form
from wtforms import (StringField, SubmitField, TextAreaField,
                     BooleanField, SelectField, IntegerField,
                     DateTimeField, FileField, SelectFieldBase)
from wtforms.validators import (Length, DataRequired,
                                Email, Regexp, ValidationError, Optional)

from ..models import Role, User, Event, Ticket


class EditProfileForm(Form):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(1, 64),
                                       Regexp(
                               '^[A-Za-z][A-Za-z0-9_.]*$', 0,
                               'Usernames must have only letters numbers, dots or underscores')])
    phone_number = StringField('Change Phone Number', validators=[
                               DataRequired(), Length(13)])
    email = StringField('Change Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_phone_number(self, field):
        if field.data != self.user.phone_number and \
                User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use.')


class EditProfileAdminForm(Form):
    role = SelectField('Edit Role', coerce=int)
    account_balance = IntegerField('Top Up')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]


class NewUserForm(Form):
    phone_number = StringField('Phone Number', validators=[
                               DataRequired(), Length(13)])
    account_balance = IntegerField('Top Up')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]

    def validate_phone_number(self, field):
        if not field.data.startswith("+"):
            raise ValidationError('Invalid Phone number format.')
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class CreateEventForm(Form):
    title = StringField('Event title', validators=[
                        Length(1, 64), DataRequired()])
    logo = FileField("Upload your event's logo/image")
    description = TextAreaField('Event description', validators=[
                                Length(0, 100), Optional()])
    location = StringField('Event City', validators=[
                           Length(0, 64), DataRequired()])
    venue = StringField('Event Venue', validators=[
                        Length(0, 64), DataRequired()])
    date = DateTimeField(
        "Event Date", format="%d/%m/%Y %H:%M", validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditEventForm(Form):
    title = StringField('Event title', validators=[
                        Length(1, 64), DataRequired()])
    logo = FileField("Choose an event logo")
    description = TextAreaField('Event description', validators=[
                                Length(0, 100), Optional()])
    location = StringField('Event City', validators=[
                           Length(0, 64), DataRequired()])
    venue = StringField('Event Venue', validators=[
                        Length(0, 64), DataRequired()])
    date = DateTimeField(
        "Event Date", format="%d/%m/%Y %H:%M", validators=[DataRequired()])
    submit = SubmitField('Update')


class CreateTicketForm(Form):
    type = SelectField('Ticket Type', coerce=int)
    price = StringField('Price of Ticket', validators=[DataRequired()])
    count = IntegerField("Number of Tickets Available",
                         validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_price(self, field):
        try:
            int(field.data)
        except:
            raise ValidationError("Price must be a valid integer.")


class EditTicketForm(Form):
    price = StringField('Price of Ticket', validators=[DataRequired()])
    count = IntegerField("Number of Tickets Available",
                         validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_price(self, field):
        try:
            int(field.data)
        except:
            raise ValidationError("Price must be a valid integer.")

    def __init__(self, ticket, *args, **kwargs):
        super(EditTicketForm, self).__init__(*args, **kwargs)
        self.ticket = ticket
