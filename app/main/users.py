from flask import render_template, abort, flash, redirect, url_for

from flask_login import login_required, current_user

from . import main
from ..decorators import admin_required
from ..models import User, db, Role
from forms import EditProfileForm, EditProfileAdminForm

@main.route('/user/<int:id>')
@login_required
def get_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    if current_user.is_administrator() or current_user == user :
        user = user
    else:
        abort(405)
    return render_template('users/user_profile.html', user=user)

@main.route("/users")
@login_required
def get_users():
    users = User.query.all()
    return render_template('users/user_list.html', users=users)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.get_user', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('users/edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        user.role = Role.query.get(form.role.data)
        user.account.balance = form.account_balance.data
        db.session.add(user)
        flash('The profile has been updated.', category="msg")
        return redirect(url_for('.get_user', id=user.id))
    form.email.data = user.email
    form.phone_number.data = user.phone_number
    form.role.data = user.role_id
    form.account_balance.data = user.account.balance
    return render_template('/users/edit_profile_admin.html', form=form, user=user)