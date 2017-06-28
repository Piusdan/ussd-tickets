from flask import request, jsonify, abort, g
from .. import db
from . import api, Permission
from .decorators import permission_Required, current_user_or_admin_required
from .errors import validation, SignupError
from ..models import User

@api.route('/user', methods=['POST'])
def create_user():
    try:
        user = User.from_json(request.json)
    except SignupError as e:
        return validation(message=e.message[0])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "new user created"}), 201


@api.route('/user/<int:id>', methods=['GET'])
@current_user_or_admin_required(id)
def get_user(id):
    """
    get a specific user from db
    :param id: 
    :return: the specified user 
    """
    user = User.query.filter_by(id=id).first_or_404()
    response = jsonify(user.to_json())
    response.status_code = 201
    return response

@api.route('/user/<int:id>', methods=['PUT'])
@current_user_or_admin_required(id)
def edit_user(id):
    """
    update user records
    :param id: 
    :return: true if update is succesfull, false otherwise
    """
    user = User.query.filter_by(id=id).first_or_404()
    data = request.json
    for k, v in data.items():
        if k:
            user.k = v

    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_json())
    response.status_code = 201
    return response


@api.route('/user', methods=['GET'])
@permission_Required(Permission.ADMINISTER)
def get_users():
    """
    get all users from the db
    :return: a paginated list of all users in the db 
    """
    users = User.query.all()
    users = [user.to_json() for user in users ]
    response = jsonify(users)
    response.status_code = 201
    return response

@api.route('/user/<int:id>', methods=['delete'])
@permission_Required(Permission.ADMINISTER)
def delete_user(id):
    """
    deletes the specified user
    :param id: 
    :return: return True if succes or False otherwise 
    """
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 201



@api.route('/user/change_role/<int:id>', methods=['PUT'])
@permission_Required(Permission.ADMINISTER)
def change_user_role(id):
    """
    change user role
    :param id: 
    :return: True if succesfull, false otherwise 
    """
    return False