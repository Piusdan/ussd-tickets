from flask_wtf import FlaskForm as Form
from wtforms import (StringField, SubmitField, TextAreaField,
                     BooleanField, SelectField, IntegerField,
                     DateTimeField, FileField, SelectFieldBase)
from wtforms.validators import (Length, DataRequired,
                                Email, Regexp, ValidationError, Optional)

from app.model import Role, User, Event, Package, Code, Interval, Message


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


class AddUserForm(Form):
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
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]

    def validate_phone_number(self, field):
        if not field.data.startswith("+"):
            raise ValidationError('Invalid Phone number format.')
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use.')
        if Code.by_code(field.data[:4]) is None:
            raise ValidationError("Please use a Kenyan or Ugandan line")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class CreateEventForm(Form):
    title = StringField('Event title', validators=[
                        Length(1, 64), DataRequired()])
    description = StringField('Event description', validators=[
                                Length(0, 100), Optional()])
    location = StringField('Event City', validators=[
                           Length(0, 64), DataRequired()])
    venue = StringField('Event Venue', validators=[
                        Length(0, 64), DataRequired()])
    date = DateTimeField(
        "Event Date", format="%d/%m/%Y", validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditEventForm(Form):
    title = StringField('Event title', validators=[
                        Length(1, 64), DataRequired()])
    description = StringField('Event description', validators=[
                                Length(0, 100), Optional()])
    location = StringField('Event City', validators=[
                           Length(0, 64), DataRequired()])
    venue = StringField('Event Venue', validators=[
                        Length(0, 64), DataRequired()])
    date = DateTimeField(
        "Event Date", format="%d/%m/%Y", validators=[DataRequired()])
    submit = SubmitField('Update')


class CreatePackageForm(Form):
    type = SelectField('Ticket Type', coerce=int)
    price = StringField('Price of Ticket', validators=[DataRequired()])
    number = IntegerField("Number of Tickets Available",
                         validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_price(self, field):
        try:
            int(field.data)
        except:
            raise ValidationError("Price must be a valid integer.")


class EditPackageForm(Form):
    price = StringField('Price of Ticket', validators=[DataRequired()])
    number = IntegerField("Number of Tickets Available",
                         validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_price(self, field):
        try:
            int(field.data)
        except:
            raise ValidationError("Price must be a valid integer.")

class CreateMessageForm(Form):
    title = StringField('Title of the Message', validators=[DataRequired()])
    body = TextAreaField('Message Body', validators=[DataRequired()])
    startdate = DateTimeField("Start", format="%d/%m/%Y", validators=[DataRequired()])
    enddate = DateTimeField("Stop", format="%d/%m/%Y", validators=[DataRequired()])
    interval = SelectField('Interval', coerce=int)
    subscriptions = FileField('Upload excel sheet of phone numbers', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CreateMessageForm, self).__init__(*args, **kwargs)
        self.interval.choices = [(interval.id, interval.name)
                             for interval in Interval.query.order_by(Interval.name).all()]

    def validate_title(self, field):
        if Message.query.filter_by(title=field.data).first() is not None:
            raise ValidationError('Message title must be unique')

