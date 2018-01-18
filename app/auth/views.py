from flask import render_template, request, redirect, flash, url_for

from flask_login import login_user, login_required, logout_user, current_user

from app.model import User, Address, Code
from app.utils.web import flash_errors, get_country
from app.auth.forms import LoginForm, RegistrationForm
from app.auth import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid email or password.', category="errors")

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category="msg")
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        city = form.city.data
        user = User(email=email, username=username, password=password, phone_number=form.phone_number.data)
        user.address = Address.create(city=city)
        country = get_country(city)
        if country is not None:
            code = Code.query.filter_by(country).first()
            if code is not None:
                user.address.code = code
        user.save()

        flash('You can now login.', category="success")
        return redirect(url_for('auth.login'))
    else:
        flash_errors(form)

    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()