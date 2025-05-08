from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models import User, db

api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'auth_type': user.auth_type
    } for user in users])

@api.route('/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        auth_type=data.get('auth_type', 'local')
    )
    
    if user.auth_type == 'local':
        user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201 