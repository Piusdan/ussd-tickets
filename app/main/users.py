from flask import render_template, abort, flash, redirect, url_for

from flask_login import login_required, current_user

from . import main
from ..utils import flash_errors
from ..decorators import admin_required
from ..controllers import async_send_message, new_user
from ..models import User, db, Role, Location
from forms import EditProfileForm, EditProfileAdminForm, NewUserForm


@main.route('/user/<int:id>')
@login_required
def get_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    has_purchases = user.account.purchases.count() > 0
    print has_purchases
    if current_user.is_administrator() or current_user == user:
        user = user
    else:
        abort(405)
    return render_template('users/user_profile.html', user=user, has_purchases=has_purchases)


@main.route("/users")
@login_required
def get_users():
    users = User.query.all()
    return render_template('users/user_list.html', users=users)


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    form = NewUserForm()
    if form.validate_on_submit():
        payload = {"username": form.username.data,
                   "phone_number": form.phone_number.data,
                   "role": form.role.data,
                   "account_balance": form.account_balance.data
                   }
        new_user(payload)
        flash('New member added.', category="success")
        return redirect(url_for('.get_users'))
    else:
        flash_errors(form)

    return render_template('users/add_user.html', form=form)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(user=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data

        current_user.about_me = form.about_me.data
        current_user.email = form.email.data 
        current_user.phone_number = form.phone_number.data 
        current_user.username = form.username.data 
        
        # get loaction
        address = form.location.data
        location = Location.query.filter_by(address=address.capitalize()).first()
        if location:
            location = location
        else:
            try:
                location = Location(address=address)
            except GeocoderError as exc:
                flash('Invalid address for user', category='errors')
        current_user.location = location
        db.session.commit()
        flash('Your profile has been updated.', category='success')
        return redirect(url_for('.get_user', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.location.city
    form.about_me.data = current_user.about_me
    form.email.data = current_user.email        
    form.phone_number.data = current_user.phone_number
    form.username.data = current_user.username 
    return render_template('users/edit_profile.html', form=form, user=current_user)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.role = Role.query.get(form.role.data)
        bal = form.account_balance.data
        if bal > 0:
            user.account.balance += bal
            message = "Cash Value Solution\nYour account has been credited with {}. {}".format(
                user.location.currency_code, form.account_balance.data)
            payload = {"message": message, "to": user.phone_number}
            async_send_message.apply_async(args=[payload], countdown=0)
        db.session.commit()
        flash('The profile has been updated.', category="successs")
        return redirect(url_for('.get_user', id=user.id))
    form.role.data = user.role_id
    form.account_balance.data = 0
    return render_template('/users/edit_profile_admin.html', form=form, user=user)
