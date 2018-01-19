from flask import render_template, abort, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from app.main import main
from app.database import db
from app.decorators import admin_required
from app.model import User, Role, Code, Address, Transaction
from app.main.utils import get_country, update_balance_and_send_sms, create_user
from app.utils.web import flash_errors
from forms import EditProfileForm, EditProfileAdminForm, AddUserForm, AddAdminForm


@main.route('/user/<string:slug>')
@login_required
def get_user(slug):
    user = User.by_slug(slug)
    form = EditProfileAdminForm(user=user)
    form.role.data = user.role_id
    form.account_balance.data = 0.00
    transactions = Transaction.query.join(User).filter(Transaction.user_id==user.id).order_by(Transaction.timestamp).all()
    if current_user.is_administrator() or current_user == user:
        user = user
    else:
        abort(405)
    return render_template('users/user.html', user=user, transactions=transactions, form=form)


@main.route("/users")
@login_required
@admin_required
def get_users():
    form = AddUserForm()
    users = User.all()
    count = len(users)
    return render_template('users/users.html', users=users, user_count=count, form=form)


@main.route('/add-user', methods=['POST'])
@login_required
@admin_required
def add_user():
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    username = request_dict['username']
    role_id = request_dict['role']
    balance = request_dict["account_balance"]
    phone_number = request_dict["phone_number"]
    if User.by_phonenumber(phone_number) is None:
        if User.by_username(username) is None:
            if phone_number.startswith('+') and Code.by_code(phone_number[:4]) is not None:
                user = User.create(role_id=role_id, username=username, phone_number=phone_number)
                code = Code.by_code(phone_number[:4])
                user.address = Address.create(code=code)
                user.account.balance = balance
                user.save()
                response = jsonify('User {} created',format(username))
                response.status_code = 201
                return response
            else:
                response = jsonify('Invalid telephone code')
        else:
            response = jsonify('Username already in use')
    else:
        response = jsonify('Phone number already in use')
    response.status_code = 300
    return response


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(user=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data 
        current_user.phone_number = form.phone_number.data 
        current_user.username = form.username.data 
        
        # get location
        city = form.location.data
        current_user.country = get_country(city)
        db.session.commit()
        flash('Your profile has been updated.', category='success')
        return redirect(url_for('.get_user', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.city
    form.email.data = current_user.email        
    form.phone_number.data = current_user.phone_number
    form.username.data = current_user.username 
    return render_template('users/edit_profile.html', form=form, user=current_user)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get(id)
    if user is None:
        response = jsonify({"payload":"User not found"})
        return response, 300
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    account_balance = float(request_dict["account_balance"])
    role_id = int(request_dict["role"])
    user.role = Role.query.get(role_id)
    if account_balance > 0:
        update_balance_and_send_sms(user, account_balance)
    response = jsonify({"payload":"User topped Up"})
    return response, 200


@main.route('/add-admin')
@login_required
@admin_required
def add_administrator():
    form = AddAdminForm()
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
        return redirect(url_for('.users'))

    return render_template('users/add-admin.html', form=form)
