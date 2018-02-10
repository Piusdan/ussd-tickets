from flask import render_template, request, redirect, flash, url_for

from flask_login import login_user, login_required, logout_user, current_user

from app.model import User, Address, Code
from app.utils.web import flash_errors, get_country
from app.auth.forms import LoginForm, ResetPasswordForm, ConfirmPasswordForm
from app.auth import auth
from ..utils.web import send_mail


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.email.data).first() or User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid phoneNumber or password.', category="errors")

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category="msg")
    return redirect(url_for('auth.login'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

@auth.route('/reset-password', methods=['POST', 'GET'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        reset_token = user.generate_reset_token()
        send_mail(to=user.email, subject='Reset Your Password', template='mail/password_reset', reset_token=reset_token,
                  user=user)
        flash('A password reset token has been sent to you by email', category='info')
        return redirect(url_for('.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/confirm-password-reset/<string:reset_token>', methods=['POST', 'GET'])
def confirm_password(reset_token):
    form = ConfirmPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        if User.reset_password(reset_token, password):
            flash('You have reset your password. Thanks!', category='info')
            return redirect(url_for('auth.login'))
        else:
            flash('The confirmation link is invalid or has expired.', category='warning')

    return render_template('auth/confirm_password.html', form=form)